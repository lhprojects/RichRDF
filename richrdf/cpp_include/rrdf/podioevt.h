#ifndef _RRDF_EDMEVT_H
#define _RRDF_EDMEVT_H


#include <vector>
#include <initializer_list>
#include "edm4hep/edm4hep.h"
#include "podio/ObjectID.h"
#include "podio/CollectionBase.h"
#include "third_party/robin_hood.h"
#include "ROOT/RDataFrame.hxx"
#include "ana.h"

namespace rrdf
{    

namespace evtd { // EVenT Details

    struct CollectionStub {

        CollectionStub() {
            //debugln("CollectionStub \n");
        }
        // it is not safe for deleter if allow copy
        CollectionStub(CollectionStub const &r) = delete;
        CollectionStub &operator=(CollectionStub const &r) = delete;

        std::unique_ptr<podio::CollectionBase> m_coll;
        std::string name;
        uint32_t collectionID;
        std::string typeName;
        void const * entries = nullptr; // std::vector<Entry>
        void (*deleter)(CollectionStub *) = nullptr;
        void (*entries_creator)(CollectionStub *) = nullptr;

        ~CollectionStub() {
            //debugln("~CollectionStub {} \n", name);
            if(deleter) {
                deleter(this);
            }
        }
    };

}

struct Event 
{
    uint64_t index = 0;
    std::vector<std::unique_ptr<evtd::CollectionStub> > collections;
    robin_hood::unordered_map<std::string_view, evtd::CollectionStub* > name_to_collection;
    robin_hood::unordered_map<uint32_t, evtd::CollectionStub* > ID_to_collection;
    robin_hood::unordered_set<uint32_t> not_found_IDs;

    std::vector<uint32_t> getNotFoundIDs() const {
        std::vector<uint32_t> ids;
        ids.reserve(not_found_IDs.size());
        for(auto id : not_found_IDs) {
            ids.push_back(id);
        }
        return ids;
    }

    template<typename Element,
        typename = std::enable_if_t< std::is_base_of<podio::CollectionBase, typename Element::collection_type>::value> 
    >
    ana::span<const Element> getElements(std::string_view name) const
    {
        evtd::CollectionStub * coll = getCollection_<typename Element::collection_type>(name);
        return *static_cast<std::vector<Element> const *>(coll->entries);
    }

    edm4hep::MCParticleCollection &getMCParticleCollection(std::string_view name) const {
        return getCollection<edm4hep::MCParticleCollection>(name);
    }

    ana::span<const edm4hep::MCParticle> getMCParticles(std::string_view name) const {
        return getElements<edm4hep::MCParticle>(name);
    }

    edm4hep::ReconstructedParticleCollection &getReconstructedParticleCollection(std::string_view name) const {
        return getCollection<edm4hep::ReconstructedParticleCollection>(name);
    }

    ana::span<const edm4hep::ReconstructedParticle> getReconstructedParticles(std::string_view name) const {
        return getElements<edm4hep::ReconstructedParticle>(name);
    }

    edm4hep::SimTrackerHitCollection &getSimTrackerHitCollection(std::string_view name) const {
        return getCollection<edm4hep::SimTrackerHitCollection>(name);
    }

    edm4hep::SimCalorimeterHitCollection &getSimCalorimeterHitCollection(std::string_view name) const {
        return getCollection<edm4hep::SimCalorimeterHitCollection>(name);
    }
    
    edm4hep::TrackCollection &getTrackCollection(std::string_view name) const {
        return getCollection<edm4hep::TrackCollection>(name);
    }

    edm4hep::ClusterCollection &getClusterCollection(std::string_view name) const {
        return getCollection<edm4hep::ClusterCollection>(name);
    }

    template<typename Collection,
        typename = std::enable_if_t< std::is_base_of<podio::CollectionBase, Collection>::value> 
    >
    Collection &getCollection(std::string_view name) const
    {
        evtd::CollectionStub * coll = getCollection_<Collection>(name);
#if 1
        if(!dynamic_cast<Collection*>(coll->m_coll.get())) {
            throw ana::exception_t(ana::format("getCollection: Collection {} is not type {}", name, 
                coll->typeName));
        }
#endif
        return *static_cast<Collection*>(coll->m_coll.get());
    }
    private:

    // we try our best to make it fast
    // but a hashtable lookup may still be needed
    // I dont like like the idea of caching the result
    // we don't use std::unordered_map because it is slow
    // we use robin_hood::unordered_map because it is faster
    template<typename Collection>
    evtd::CollectionStub *getCollection_(std::string_view name) const
    {
        auto it = name_to_collection.find(name);
        if(it == name_to_collection.end()) {
            throw ana::exception_t(ana::format("getCollection_: Collection {} not found", name));
        }
        evtd::CollectionStub * coll = it->second;
#if 0        
        char const *typeName = evtd::getTypeName<Collection>();
        // strlen(typeName) == 0, we don't know the type
        // if we don't know the type, we can't check it
        // Good luck to the user
        if((strlen(typeName) != 0) && (coll->typeName != typeName)) {
            throw ana::exception_t(ana::format("getCollection_: Collection {} is not type {}", name, typeName));
        }
#endif
        return coll;
    }  
};

namespace evtd {

#if 1
template<typename Entry>
void deleter(CollectionStub *ptr) {
    if(ptr) {
        if(ptr->entries) {
            auto *entries = static_cast<std::vector<Entry> const *>(ptr->entries);
            delete entries;
        }    
    }
}

template<typename Entry>
void entries_creator(CollectionStub *coll_) {
    if(coll_) {
        auto *coll = static_cast<typename Entry::collection_type*>(coll_->m_coll.get());
        size_t coll_size = coll->size();
        std::vector<Entry> *entries = new std::vector<Entry>();
        entries->reserve(coll_size);
        for(int i = 0; i < (int)coll_size; i++) {
            entries->emplace_back((*coll)[i]);
        }
        coll_->entries = entries;
    }
}

// we take ownership of coll
inline CollectionStub *_addCollection(Event &self, std::string_view name, podio::CollectionBase* coll, uint32_t collectionID, std::string_view typeName)
{
    auto ptr = std::make_unique<CollectionStub>();
    ptr->m_coll.reset(coll);
    ptr->name = name;
    ptr->typeName = typeName;
    ptr->collectionID = collectionID;

    coll->setID(collectionID);
    
    CollectionStub *ptr_ = ptr.get();
    self.name_to_collection[ptr->name] = ptr_;    // ptr->name will long live
    self.ID_to_collection[collectionID] = ptr_;   // after move, result of ptr.get() here is still valid
    self.collections.push_back(std::move(ptr));
    return ptr_;
}


template<class Collection>
void addCollection(Event &self, std::string_view name, Collection* coll, uint32_t collectionID, std::string_view typeName)
{
    using Entry = typename Collection::value_type;
    CollectionStub *coll_ = _addCollection(self, name, coll, collectionID, typeName);

    coll_->entries = nullptr;    
    coll_->deleter = evtd::deleter<Entry>;
    coll_->entries_creator = evtd::entries_creator<Entry>;
}

struct Options {
    bool throwExceptionOnRefCollIDNotFound = false;
    char const *(*getCollNameById)(uint32_t ID) = nullptr;
};


class LookupCollectionProvider : public podio::ICollectionProvider {
    public:
        Event *m_event;
        mutable uint32_t last_ID = -1;
        mutable uint32_t last_return = -1;
        mutable podio::CollectionBase *last_collection = nullptr;
        Options const &options;
        std::string_view current_collection;

        LookupCollectionProvider(Event *base, Options const &options) : m_event(base), options(options)
         { }
    
      bool get(uint32_t collectionID, podio::CollectionBase*& collection) const override {
        

        //debugln("get collectionID {} last collectionID {} \n", collectionID, last_ID);
        if(collectionID == last_ID) {
            //debugln("cached result \n");
            if(last_return) {
                collection = last_collection;
            }
            return last_return;
        }

        last_ID = collectionID;
        auto it = m_event->ID_to_collection.find(collectionID);
        if(it == m_event->ID_to_collection.end()    ) {
            
            last_collection = nullptr;
            last_return = false;
            
            m_event->not_found_IDs.insert(collectionID);

            if (options.throwExceptionOnRefCollIDNotFound) {                
                char const *collName = "";
                if(options.getCollNameById) {
                    collName = options.getCollNameById(collectionID);
                };
                throw ana::exception_t(ana::format(
                    "Collection {name} ({}) not found, requested by `{}'. Add it to `ReadEvent' if it exists", 
                    collName,
                    collectionID,
                    current_collection));
            }

            return false;
        } else {
            last_collection = it->second->m_coll.get();
            last_return = true;

            collection = last_collection;
            return true;
        }

      }
};
    

template<typename CollectionData, typename Collection, typename EntityData>
struct CollectionReader
{

    static void readSubColl(Event &event,
        std::string_view collName_,
        uint32_t collID,
        std::string_view collType,
        std::initializer_list< ROOT::VecOps::RVec<podio::ObjectID> const*> rels) {

        podio::CollRefCollection * refColl = new podio::CollRefCollection();
        for(int i = 0; i < (int)rels.size(); i++) {
            ROOT::VecOps::RVec<podio::ObjectID> const *v = rels.begin()[i];
            refColl->emplace_back(std::make_unique<std::vector<podio::ObjectID> >(v->begin(), v->end())); // we have copy here
        }
        //print("size of rels {} \n", refColl->begin()[0]->size());

        std::vector<EntityData> *mcps_data = 
                    new std::vector<EntityData>(); 

        podio::VectorMembersInfo *memoryMemberInfo = new podio::VectorMembersInfo();

        podio::CollectionReadBuffers buffer((void*)mcps_data,  
                    refColl,
                    memoryMemberInfo,
                    podio::SchemaVersionT(),
                    "",
                    podio::CollectionReadBuffers::CreateFuncT(),
                    podio::CollectionReadBuffers::RecastFuncT(),
                    podio::CollectionReadBuffers::DeleteFuncT()
                );
            
        CollectionData collData(std::move(buffer), true);
        Collection *coll = new Collection(std::move(collData), true);
                
        coll->prepareAfterRead();    
        addCollection<Collection>(event, collName_, coll, collID, collType);

    }

    static void read(Event &event,
        std::string_view collName_,
        uint32_t collID,
        std::string_view collType,
        void const* data,
        std::initializer_list< ROOT::VecOps::RVec<podio::ObjectID> const*> rels,
        std::initializer_list< std::string_view> memVecName,
        std::initializer_list< void *> memVec // std::vector<xxxx> const *
    ) {

        std::unique_ptr<Collection> coll = readCollection(event, data, rels, memVecName, memVec);
        addCollection<Collection>(event, collName_, coll.release(), collID, collType);
    }
    
    static std::unique_ptr<Collection>
    readCollection(Event &event,
        void const* data,
        std::initializer_list< ROOT::VecOps::RVec<podio::ObjectID> const*> rels,
        std::initializer_list< std::string_view> memVecName,
        std::initializer_list< void *> memVec // std::vector<xxxx> const *
    )
    {
        ROOT::VecOps::RVec<EntityData> const &entities = 
            *static_cast<ROOT::VecOps::RVec<EntityData> const *>(data);

        podio::CollRefCollection * refColl = new podio::CollRefCollection();
        for(int i = 0; i < (int)rels.size(); i++) {
            ROOT::VecOps::RVec<podio::ObjectID> const *v = rels.begin()[i];
            refColl->emplace_back(std::make_unique<std::vector<podio::ObjectID> >(v->begin(), v->end())); // we have copy here
        }

        std::vector<EntityData> *mcps_data = 
                    new std::vector<EntityData>(entities.begin(), entities.end()); // we have copy here

        podio::VectorMembersInfo *memoryMemberInfo = new podio::VectorMembersInfo();
        for (size_t i = 0; i < memVec.size(); ++i) {
            memoryMemberInfo->emplace_back(std::make_pair(memVecName.begin()[i], memVec.begin()[i]));
        }

        podio::CollectionReadBuffers buffer((void*)mcps_data,  
                    refColl,
                    memoryMemberInfo,
                    podio::SchemaVersionT(),
                    "",
                    podio::CollectionReadBuffers::CreateFuncT(),
                    podio::CollectionReadBuffers::RecastFuncT(),
                    podio::CollectionReadBuffers::DeleteFuncT()
                );
            
        CollectionData collData(std::move(buffer), false);
        Collection *coll = new Collection(std::move(collData), false);
                
        coll->prepareAfterRead();    
        return std::unique_ptr<Collection>(coll);
    }
};

void setup_Ref(Event &event, const Options &options) {

    LookupCollectionProvider prov(&event, options);

    for(auto const &coll : event.collections) {
        prov.current_collection = coll->name;
        coll->m_coll->setReferences(&prov);
    }

    for(auto const &coll : event.collections) {
        coll->entries_creator(coll.get());
    }
}


#else

template<typename CollectionData, typename Collection, typename EntityData>
struct CollectionReader
{

    static void read(Event &event,
        std::string_view collName_,
        uint32_t collID,
        std::string_view collType,
        void const* data,
        std::initializer_list< ROOT::VecOps::RVec<podio::ObjectID> const*> rels) {
        print("WARNING: No collection will be read by configration");
    }
};

void setup_Ref(Event &event) {
}
#endif

} // namespace evtd

} // namespace ana

#endif
