from collections.abc import Iterable
from collections import namedtuple
import glob
import json

CollTypeInfo = namedtuple("CollTypeInfo", ["name", "id", "isSubColl", "version"])

def getRelBranches(podio_metadata):
    relBranches = {}

    # from long long to short name
    # so that we can deal with a, _a_b_, a_b_, _a_b_c correctly
    # note: in this case, we have two collections, a, and a_b
    branchNames_sorted = sorted(podio_metadata.branchNames)[::-1]
    branchNames_origin = podio_metadata.branchNames
    branchNames_set = set(podio_metadata.branchNames)
    deleted = [False] * len(branchNames_origin)

    for collName in branchNames_sorted:
        if collName not in podio_metadata.events_colls_name:
            continue
        
        if collName not in branchNames_set:
            raise ValueError(f"Collection {collName} is a collection name, but not a branch name ({branchNames_origin})")

        start = "_" + collName + "_"
        relBranches[collName] = []

        # use origin order
        for i, branchName in enumerate(branchNames_origin):
            if not deleted[i] and branchName.startswith(start):
                relBranches[collName].append(branchName)
                deleted[i] = True
        
    return relBranches

def getRelBranchesFromDefs(podio_metadata):
    relBranches = {}

    for _, typeRels in podio_metadata.edm_defs.items():
        for typeName, rel in typeRels.items():

            relBranches[typeName + "Collection"] = []
            if "OneToManyRelations" in rel:
                for r in rel["OneToManyRelations"]:
                    relBranches[typeName + "Collection"].append(r["name"])
            
            if "OneToOneRelations" in rel:
                for r in rel["OneToOneRelations"]:
                    relBranches[typeName + "Collection"].append(r["name"])

    #print(json.dumps(relBranches, indent=4))
    return relBranches

def getVecMembersFromDefs(podio_metadata):
    relBranches = {}

    for _, typeRels in podio_metadata.edm_defs.items():
        for typeName, rel in typeRels.items():
            relBranches[typeName + "Collection"] = []
            if "VectorMembers" in rel:
                for r in rel["VectorMembers"]:
                    relBranches[typeName + "Collection"].append(r)

    return relBranches


class PODIO_Metadata:
    def __init__(self, coll_type_infos, events_colls_name, events_colls_id, edm_defs, branchNames):
        self.coll_type_infos = coll_type_infos
        self.events_colls_name = events_colls_name
        self.events_colls_id = events_colls_id
        self.edm_defs = edm_defs
        self.branchNames = branchNames

        self.events_id_to_name = {}
        self.events_name_to_id = {}
        self.colls_id_to_type  = {}

        for id, name in zip(events_colls_id, events_colls_name):
            self.events_id_to_name[id] = name
            self.events_name_to_id[name] = id
        
        for info in coll_type_infos:
            id, name, isSubColl, version = info
            self.colls_id_to_type[id] = CollTypeInfo(name, id, isSubColl, version)

        #self.relBranches = getRelBranches(self)
        self.relBranches = getRelBranchesFromDefs(self)
        self.vecMembers = getVecMembersFromDefs(self)
    
    def getCollTypeInfos(self):
        '''
        Get the collection type information.
        '''
        return self.coll_type_infos    
    
    def getCollInfo(self):
        '''
        Get the collection type information.
        '''
        return [(name, id) for name, id in zip(self.events_colls_name, self.events_colls_id)]
    
    def getBranchNames(self):
        '''
        Get the names of all branches.
        '''
        return self.branchNames
    
    def collNames(self):
        '''
        Get the names of all collections.
        '''
        return self.events_colls_name
    
    def getIDByName(self, name) -> int:
        '''
        Get the ID of a collection by its name.
        '''
        if name not in self.events_name_to_id:
            raise ValueError(f"Collection {name} not found in metadata ({self.events_colls_name})")
        
        id = self.events_name_to_id[name]
        return id

    def getNameByID(self, id):
        '''
        Get the name of a collection by its ID.
        '''
        if id not in self.events_id_to_name:
            raise ValueError(f"Collection {id} not found in metadata ({self.events_colls_name})")
        
        name = self.events_id_to_name[id]
        return name
    
    def getTypeByID(self, id):
        '''
        Get the type of a collection by its ID.
        '''
        if id not in self.colls_id_to_type:
            raise ValueError(f"Collection type for Collection {id} not found in metadata")
        
        type = self.colls_id_to_type[id]
        return type

    def getTypeByName(self, name):
        '''
        Get the type of a collection by its name.
        '''
        id = self.getIDByName(name)
        if id not in self.colls_id_to_type:
            raise ValueError(f"Collection type for Collection {name} with ID {id} not found in metadata")
        
        type = self.colls_id_to_type[id]
        return type

def get_defs_from_tree(tree):

    EDMDefinitions = tree.EDMDefinitions
    rels_defs = {}
    for de in EDMDefinitions:
        namespace = str(de._0)
        content = str(de._1)
        
        rels_defs_name={}
        rels_defs[namespace] = rels_defs_name
        js = json.loads(content)
        #print(json.dumps(js, indent=4))
        if "datatypes" in js:
            datatypes = js["datatypes"]
            for typeName, typeDef in datatypes.items():
                
                one2ManyRels=[]
                one2OneRels=[]
                vectorMems=[]
                if "OneToManyRelations" in typeDef:
                    OneToManyRelations = typeDef["OneToManyRelations"]    
                    for rel in OneToManyRelations:
                        sps = rel.split(" ")
                        one2ManyRel = {"type": sps[0], "name": sps[1]}
                        one2ManyRels.append(one2ManyRel)

                if "OneToOneRelations" in typeDef:
                    OneToOneRelations = typeDef["OneToOneRelations"]    
                    for rel in OneToOneRelations:
                        sps = rel.split(" ")
                        one2OneRel = {"type": sps[0], "name": sps[1]}
                        one2OneRels.append(one2OneRel)
                if "VectorMembers" in typeDef:
                    VectorMembers = typeDef["VectorMembers"]    
                    for rel in VectorMembers:
                        sps = rel.split(" ")
                        vectorMem = {"type": sps[0], "name": sps[1]}
                        vectorMems.append(vectorMem)

                rels_defs_name[typeName] = {"OneToManyRelations": one2ManyRels, 
                                        "OneToOneRelations": one2OneRels,
                                        "VectorMembers": vectorMems}
                
    #print(json.dumps(rels_defs, indent=4))
    return rels_defs

def get_podio_metadata(file):
    import ROOT
    tree = file.Get("podio_metadata")
    entry = tree.GetEntry(0) # cursor to the first entry

    coll_type_infos = []
    for i in range(len(tree.events___CollectionTypeInfo)):
        info = tree.events___CollectionTypeInfo[i]
        info = (int(info._0), info._1.decode('utf-8'), int(info._2), int(info._3))
        coll_type_infos.append(info)

    events_colls_name = [str(v) for v in tree.events___idTable.names()]
    events_colls_id = [int(v) for v in tree.events___idTable.ids()]
    rel_defs = get_defs_from_tree(tree)

    
    tree = file.Get("events")
    branches = tree.GetListOfBranches()
    branchNames = [ str(b.GetName()) for b in branches]

    return PODIO_Metadata(coll_type_infos, events_colls_name, events_colls_id, rel_defs, branchNames)


def _is_string_like(obj):
    return isinstance(obj, str)

def _is_list_like(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes))



def ReadPODIO_Metadata(fileName):
    import ROOT
    
    if _is_string_like(fileName):
        fileName = [fileName]

    assert _is_list_like(fileName), "fileName must be a string or a list of strings"
    
    fileNames = []
    for filename_ in fileName:
        assert _is_string_like(filename_), f"fileName must be a string or a list of strings, got {type(filename_)}"
        fileNames.extend(glob.glob(filename_))

    assert len(fileNames) > 0, "No file at all"

    file = ROOT.TFile.Open(fileNames[0])
    try:
        metadata = get_podio_metadata(file)
    except Exception as e:
        raise e
    finally:
        file.Close()

    return metadata

def init_Metadata(*kargs, **kwargs):
    if len(kargs) >= 2:
        fileName = kargs[1]
    elif "filenameglob" in kwargs:
        fileName = kwargs["filenameglob"]
    elif "filename" in kwargs:
        fileName = kwargs["filename"]
    elif "filenames" in kwargs:
        fileName = kwargs["filenames"][0]
    else:
        raise ValueError("fileName not found in arguments")

    metadata = ReadPODIO_Metadata(fileName)
    return metadata

    
def ReadEventDefintion(df, podio_metadata: PODIO_Metadata, collections, 
                       throwExceptionOnRefCollIDNotFound: bool = False):


    if collections is None or len(collections) == 0:
        collections = []
        for collName, id in podio_metadata.events_name_to_id.items():
            if id not in podio_metadata.colls_id_to_type:
                print(f"Collection {collName} with ID {id} has no type information, skipping")     
                continue
            
            collType = podio_metadata.colls_id_to_type[id]
            if collType.name not in podio_metadata.relBranches:
                print(f"Collection {collName} with type {collType.name} has no edm defintion, skipping")
                continue
            
            if not collType.isSubColl:
                if collName not in podio_metadata.branchNames:
                    print(f"Collection {collName} has no branch name, skipping")
                    continue
            else:
                if collName + "_objIdx" not in podio_metadata.branchNames:
                    print(f"Collection {collName} has no branch name ({collName + '_objIdx'}), skipping")
                    continue

            collections.append(collName)

    collTypeNames = []
    collIds = []
    isSubcoll = []
    for collName in collections:
        collId = podio_metadata.getIDByName(collName)
        #collType = podio_metadata.getTypeByID(collId)
        collType = podio_metadata.getTypeByName(collName)
        collIds.append(collId)
        collTypeNames.append(collType.name)
        isSubcoll.append(collType.isSubColl)

    def get_for_normal_collection(collName, collID, collType):
        relBranches = podio_metadata.relBranches
        vecMembers = podio_metadata.vecMembers
        branches_relations = relBranches[collType]
        branches_relations = [ "_" + collName + "_" + br for br in branches_relations ]
        str_rel_branches = "".join(f'&{brName}, //// {brName[:-1]}\n' for brName in branches_relations)

        memVec = vecMembers[collType]

        memVecTypeName = [ br["type"] for br in memVec ]
        strMemVecTypeName = "".join([ f'"{typeName}", ' for typeName in memVecTypeName ])
        memVecName = [ br["name"] for br in memVec ]
        memVecBrName = [ "_" + collName + "_" + br for br in memVecName ]

        memArray=[]
        for typeName, brName in zip(memVecTypeName, memVecBrName):
            memArray.append(f"new std::vector< {typeName} >({brName}.data(), {brName}.data() + {brName}.size()), // {brName[:-1]}\n")

        strMemArray = "".join(memArray)

        # You dont want MCParticle to be replaced by the var0???
        collName1 = collName[:-1]
        collName2 = collName[-1:]

        
        return f'''
        do {{
            using EntityData = {collType[:-len("Collection")]}Data;
            using CollectionData = {collType}Data;
            using Collection = {collType};

            using Reader = rrdf::evtd::CollectionReader<CollectionData, Collection, EntityData>;
        
            ROOT::VecOps::RVec<EntityData> const &entities = {collName}; // {collName1} {collName2}

            std::initializer_list< ROOT::VecOps::RVec<podio::ObjectID> const* >  rels = {{ 
            {str_rel_branches} 
            }};

            std::initializer_list< std::string_view> memVecName = {{
            {strMemVecTypeName}
            }};

            std::initializer_list< void *> memVec  = {{ // std::vector<xxxx> *
            {strMemArray}
            }};
            
            char const *collName_ = "{collName1}"  "{collName2}"; // concatenate the strings
            Reader::read(event, collName_, {collID}, "{collType}", &entities, 
                rels, memVecName, memVec);

        }} while(0);
'''

    def get_for_sub_collection(collName, collID, collType):
        # You dont want MCParticle to be replaced by the var0???
        collName1 = collName[:-1]
        collName2 = collName[-1:]

        return f'''
        do {{
            using EntityData = {collType[:-len("Collection")]}Data;
            using CollectionData = {collType}Data;
            using Collection = {collType};

            using Reader = rrdf::evtd::CollectionReader<CollectionData, Collection, EntityData>;
                    
            std::initializer_list< ROOT::VecOps::RVec<podio::ObjectID> const* >  rels = {{ 
            &{collName}_objIdx, // {collName1} {collName2}
            }};

            char const *collName_ = "{collName1}"  "{collName2}"; // concatenate the strings
            Reader::readSubColl(event, collName_, {collID}, "{collType}", rels);

        }} while(0);
'''

    body = ""
    for collName, collID, collTypeName, isSubcoll_ in zip(collections, collIds, collTypeNames, isSubcoll):
        if not isSubcoll_:
            body += get_for_normal_collection(collName, collID, collTypeName)

    for collName, collID, collTypeName, isSubcoll_ in zip(collections, collIds, collTypeNames, isSubcoll):
        if isSubcoll_:
            body += get_for_sub_collection(collName, collID, collTypeName)

    # this just works, it seems the return key in the function body

    collNames = "".join([f'"{coll[:-1]}" "{coll[-1:]}",\n' for coll in podio_metadata.events_colls_name])
    collIDs = "".join([f'{collID},\n' for collID in podio_metadata.events_colls_id])
    function_body ='''
    {
    rrdf::Event event;
'''  + body +  f'''

    char const *(*getCollNameById)(uint32_t ID) = [](uint32_t ID) -> char const * {{
        char const *names[] = {{
            {collNames}
        }};
        uint32_t IDs[] = {{
            {collIDs}
        }};
        for(int i = 0; i < sizeof(IDs)/sizeof(uint32_t); ++i) {{
            if (IDs[i] == ID) {{
                return names[i];
            }}
        }}
        return "Unknown";
    }};
    
    rrdf::evtd::Options options;
    options.getCollNameById = getCollNameById;
    options.throwExceptionOnRefCollIDNotFound = {"true" if throwExceptionOnRefCollIDNotFound else "false"};
    rrdf::evtd::setup_Ref(event, options);
    return std::move(event);
''' + "}"

    generate_function = f'''{function_body}'''
    # NO, this didn't work
    #generate_function = f'''[&]() -> ana::Event {{ return {function_body}; }}()'''
    return generate_function

def _ReadEvent(df, metadata, eventName: str, collections: list = None, 
               printGeneratedCode:bool = False, throwExceptionOnRefCollIDNotFound: bool = False):
    generate_function = ReadEventDefintion(df, metadata, collections, 
                        throwExceptionOnRefCollIDNotFound=throwExceptionOnRefCollIDNotFound)

    if printGeneratedCode:
        print(generate_function)

    import ROOT
    ROOT.gInterpreter.Declare('#include "rrdf/podioevt.h"')
    return df.Define(eventName, generate_function)

