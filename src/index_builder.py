from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core import StorageContext
from src.global_settings import INDEX_STORAGE

def build_indexes(nodes):
    """
        Hàm tải hoặc tạo index để tìm kiếm trên các tài liệu đã xử lý.
        Nếu đã tồn tại index trong lưu trữ, hàm sẽ tải các index từ storage.
        Nếu không, hàm sẽ tạo index mới từ dữ liệu đầu vào (`nodes`) và lưu lại.

        Parameters:
            nodes (list): Danh sách các node chứa nội dung đã xử lý từ tài liệu.

        Returns:
            vector_index (VectorStoreIndex): Đối tượng index để tìm kiếm.
        """
    try:
        # tải context của storage từ thư mục đã chỉ định
        storage_context = StorageContext.from_defaults(
            persist_dir=INDEX_STORAGE
        )
        # Tải index vector từ storage theo ID "vector"
        vector_index = load_index_from_storage(
            storage_context, index_id="vector"
        )
        print("Tải index thành công từ kho lưu trữ")
    except Exception as e:
        # Nếu lỗi xảy ra, tạo index mới từ `nodes`
        print(f"Đã xảy ra lỗi khi tải index: {e}")
        # Khởi tạo storage context mới để tạo index mới
        storage_context = StorageContext.from_defaults()
        # Tạo vector index từ `nodes` và gán vào storage_context
        vector_index = VectorStoreIndex(
            nodes, storage_context=storage_context
        )
        vector_index.set_index_id("vector")
        # Lưu storage_context và index vào thư mục chỉ định
        storage_context.persist(
            persist_dir=INDEX_STORAGE
        )
        print("Index mới đã được tạo và lưu thành công")
    return vector_index




