from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
import os
import dotenv

# Make sure to set your OpenAI API key
dotenv.load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

def create_and_query_index():
    # Define storage directory
    storage_dir = "./vector"

    # Check if index already exists
    if not os.path.exists(storage_dir):
        # Load documents from a directory
        documents = SimpleDirectoryReader("""C:\\Users\\jackm\\Development\\LlamaTime\\data""").load_data()

        # Create an index from the documents
        index = VectorStoreIndex.from_documents(documents)

        # Create storage directory and save index
        os.makedirs(storage_dir, exist_ok=True)
        index.storage_context.persist(persist_dir=storage_dir)
    else:
        # Load existing index
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context)

    # Create a query engine
    query_engine = index.as_query_engine()

    # Perform a query
    response = query_engine.query("Who is the quarterback of the New York Giants?")

    print(response)

if __name__ == "__main__":
    create_and_query_index()