from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import openai
import streamlit as st
from src.global_settings import STORAGE_PATH, FILES_PATH, CACHE_FILE
from src.prompts import CUSTOM_SUMMARY_EXTRACT

openai.api_key = st.secrets.openai.OPENAI_API_KEY
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.2)


def ingest_documents():
    """
        Nạp và xử lý các tài liệu từ thư mục chỉ định, chia nhỏ dữ liệu, tạo tóm tắt và tạo embedding để phục vụ tìm kiếm.
        Sử dụng cache (nếu có) để tối ưu hóa thời gian xử lý nếu tài liệu đã được xử lý trước đó.

        Returns:
            nodes (list): Danh sách các `node` chứa nội dung đã chia nhỏ, tóm tắt và embedding từ các tài liệu.
        """
    # Tải tài liệu từ thư mục, gán ID dựa trên tên file cho mỗi tài liệu.
    # Sử dụng input_files để xác định thư mục chứa các file tài liệu đầu vào.
    documents = SimpleDirectoryReader(
        input_files=FILES_PATH,
        filename_as_id=True
    ).load_data()

    # In ra ID của từng tài liệu đã tải
    for doc in documents:
        print(doc.id_)

    # Kiểm tra xem cache đã tồn tại chưa
    try:
        # Nếu file cache tồn tại, nạp cache từ file này để tiết kiệm thời gian xử lý
        cached_hashes = IngestionCache.from_persist_path(CACHE_FILE)
        print("Đã tìm thấy file cache. Đang chạy bằng file cache...")
    except FileNotFoundError:
        # Nếu không có cache, chạy quy trình xử lý từ đầu
        cached_hashes = None
        print("Không tìm thấy file cache. Chạy lại quy trình...")

    # Thiết lập pipeline xử lý dữ liệu với các bước:
    # - Chia nhỏ văn bản thành các đoạn với kích thước 512 token, chồng lấp 20 token.
    # - Trích xuất tóm tắt với mẫu (template) tuỳ chỉnh cho mỗi đoạn văn bản.
    # - Tạo embedding cho mỗi đoạn văn bản đã chia nhỏ.
    pipeline = IngestionPipeline(
        transformations=[
            TokenTextSplitter(
                chunk_size=512,
                chunk_overlap=20
            ),
            SummaryExtractor(summaries=['self'], prompt_template=CUSTOM_SUMMARY_EXTRACT),
            OpenAIEmbedding()
        ],
        cache=cached_hashes
    )

    # Chạy pipeline trên các tài liệu đã tải, thực hiện chia nhỏ, tóm tắt, và tạo embedding
    nodes = pipeline.run(documents=documents)

    # Lưu cache lại để tái sử dụng trong các lần chạy tiếp theo
    pipeline.cache.persist(CACHE_FILE)

    # Trả về các `node` đã xử lý với nội dung chia nhỏ, tóm tắt và embedding
    return nodes
