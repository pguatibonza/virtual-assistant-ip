import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PDFMinerLoader
from langchain_openai import AzureOpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from supabase import create_client, Client
from langchain_community.vectorstores import SupabaseVectorStore
import logging
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain.indexes import SQLRecordManager, index
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.document_loaders import DirectoryLoader
#Variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME=os.getenv("TABLE_NAME")

embeddings= AzureOpenAIEmbeddings(azure_deployment="gpt4-embedding-ada-002")
# Crear cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(f"Supabase client initialized: {supabase}")

#Crear indice para evitar duplicados
namespace=f"documents/{TABLE_NAME}"
record_manager=SQLRecordManager(namespace,db_url="sqlite:///record_manager_cache.sql")
#linea que toca colocar la primera vez que se cree el indice : 
#record_manager.create_schema()

#Carga el vector store de la base de datos
def load_vector_store():
    vector_store = SupabaseVectorStore(
        embedding=embeddings,
        table_name=TABLE_NAME,
        client=supabase,
        query_name="match_documents",
    )
    return vector_store


#Elimina caracteres no deseados
def clean_data(documents):
    for document in documents:
        document.page_content=document.page_content.replace("\u0000","")
    return documents


def load_file_headers(file_path):
    loader = UnstructuredMarkdownLoader(file_path)
    document=loader.load()
    document=clean_data(document)

    logging.info("Documento cargado en langchain")
    headers=[("#","Header1"), ("##","Header2"),("###","Header3")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers)
    docs=markdown_splitter.split_text(document[0].page_content)
    return docs

#Carga un directorio completo
def load_directory(directory,breakpoint_type="percentile"):
    #Carga los archivos desde un directorio 
    loader=DirectoryLoader(directory,glob="**/*.md",loader_cls=UnstructuredMarkdownLoader,show_progress=True)
    documents=loader.load()
    documents=clean_data(documents)
    logging.info("documentos cargados en langchain")

    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type=breakpoint_type)
    docs=text_splitter.create_documents([document.page_content for document in documents ],metadatas=[document.metadata for document in documents] )
    
    #Obtener la base de datos
    vector_store = load_vector_store()
    
    #Crear el indice para evitar duplicados
    print(index(docs,record_manager,vector_store,cleanup="incremental",source_id_key="source"))

    logging.info("Documentos insertados correctamente en la base de datos")
    return docs

# Gradient o percentile son buenas opciones
def load_file_semantic(file_path, breakpoint_type="percentile"):
    loader = UnstructuredMarkdownLoader(file_path)
    document=loader.load()
    document=clean_data(document)
    logging.info("Documento cargado en langchain")

    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type=breakpoint_type)
    docs=text_splitter.create_documents([document[0].page_content],metadatas=[document[0].metadata] )
    
    #Obtener la base de datos
    vector_store = load_vector_store()
    
    #Crear el indice para evitar duplicados
    print(index(docs,record_manager,vector_store,cleanup="incremental",source_id_key="source"))

    logging.info("Documentos insertados correctamente en la base de datos")
    return docs

#documents=load_directory("data/")


