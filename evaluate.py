import openai
from llama_index.core import Settings, Document, VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.evaluation import (
    BatchEvalRunner,
    CorrectnessEvaluator,
    FaithfulnessEvaluator,
    RelevancyEvaluator
)
from llama_index.core.llama_dataset.generator import RagDatasetGenerator
import asyncio
import pandas as pd
import nest_asyncio
from tqdm.asyncio import tqdm_asyncio
import streamlit as st
from src import ingest_pipeline, index_builder
import os

# Khởi tạo OpenAI
def setup_openai(api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.2):
    if api_key:
        openai.api_key = api_key
        Settings.llm = OpenAI(model=model, temperature=temperature)
    else:
        st.error("API Key của OpenAI không khả dụng. Vui lòng kiểm tra cấu hình API.")

# sinh cu hỏi đánh giá từ nodes
def generate_questions(nodes, num_questions_per_chunk: int = 1):
    st.info("Đang tạo câu hỏi đánh giá...")
    dataset_generator = RagDatasetGenerator(nodes, num_questions_per_chunk=num_questions_per_chunk)
    eval_questions = dataset_generator.generate_questions_from_nodes()
    st.success("Đã tạo câu hỏi thành công.")
    return eval_questions.to_pandas()

# Hàm bất đồng bộ để đánh giá câu trả lời
async def evaluate_async(query_engine, df):
    st.info("Đang tiến hành đánh giá bất đồng bộ...")

    # Đánh giá độ chính xác so với câu trả lời tham chiếu. Giá trị từ 1-5
    correctness_evaluator = CorrectnessEvaluator()

    # Đánh giá phản hồi có nhất quán với thông tin gốc không (tránh hallucination). Giá trị từ 0-1
    faithfulness_evaluator = FaithfulnessEvaluator()

    # Đánh giá câu trả lời có thực sự trả lời câu hỏi được đưa ra hay không. Giá trị từ 0-1
    relevancy_evaluator = RelevancyEvaluator()

    # Khởi tạo BatchEvalRunner
    runner = BatchEvalRunner(
        {
            "correctness": correctness_evaluator,
            "faithfulness": faithfulness_evaluator,
            "relevancy": relevancy_evaluator
        },
        show_progress=True
    )

    # Thực hiện đánh giá bất đồng bộ với các câu hỏi từ DataFrame
    eval_result = await runner.aevaluate_queries(
        query_engine= query_engine,
        queries=[question for question in df['query']],
    )

    return eval_result

# Tổng hợp kết quả đánh giá
def aggregate_results(df, eval_result):
    data = []
    for i, question in enumerate(df['query']):
        # Lấy kết quả từ từng tiêu chí
        correctness_result = eval_result['correctness'][i]
        faithfulness_result = eval_result['faithfulness'][i]
        relevancy_result = eval_result['relevancy'][i]

        # Tổng hợp dữ liệu từng câu hỏi
        data.append({
            'Query': question,
            'Correctness response': correctness_result.response,
            'Correctness passing': correctness_result.passing,
            'Correctness feedback': correctness_result.feedback,
            'Correctness score': correctness_result.score,
            'Faithfulness response': faithfulness_result.response,
            'Faithfulness passing': faithfulness_result.passing,
            'Faithfulness feedback': faithfulness_result.feedback,
            'Faithfulness score': faithfulness_result.score,
            'Relevancy response': relevancy_result.response,
            'Relevancy passing': relevancy_result.passing,
            'Relevancy feedback': relevancy_result.feedback,
            'Relevancy score': relevancy_result.score,
        })

    # Trả về bảng dữ liệu chứa tất cả các kết quả
    df_result = pd.DataFrame(data)
    return df_result

# Tính toán và in điểm trung bình
def print_average_scores(df):
    correctness_scores = df['Correctness score'].mean()
    faithfulness_scores = df['Faithfulness score'].mean()
    relevancy_scores = df['Relevancy score'].mean()
    print(f"Correctness scores: {correctness_scores}")
    print(f"Faithfulness scores: {faithfulness_scores}")
    print(f"Relevancy scores: {relevancy_scores}")
    return correctness_scores, faithfulness_scores, relevancy_scores

def main():
    # Cho phép asyncio hoạt động trong môi trường Streamlit
    nest_asyncio.apply()

    # Lấy API Key từ file cấu hình Streamlit
    api_key = st.secrets.openai.OPENAI_API_KEY

    # Thiết lập API OpenAI
    setup_openai(api_key=api_key)

    # Ingest tài liệu và chia nhỏ thành các node
    nodes = ingest_pipeline.ingest_documents()

    # tạo vector store index và query engine
    index = index_builder.build_indexes(nodes)
    dsm5_engine = index.as_query_engine(
        similarity_top_k=3,
    )

    # Sinh các câu hỏi đánh giá từ node
    df = generate_questions(nodes)

    # Thực hiện đánh giá chatbot
    eval_result = asyncio.run(evaluate_async(query_engine=dsm5_engine, df=df))

    # Tổng hợp kết quả đánh giá
    df_result = aggregate_results(df, eval_result)

    # Tính và in điểm trung bình
    correctness_scores, faithfulness_scores, relevancy_scores = print_average_scores(df_result)
    
    # Lưu kết quả đánh giá vào thư mục `eval_results`
    os.makedirs("eval_results", exist_ok=True)
    df_result.to_csv("eval_results/evaluation_results.csv", index=False)
    df.to_csv("eval_results/evaluation_questions.csv", index=False)

    # Lưu điểm trung bình vào file txt
    with open("eval_results/average_scores.txt", "w") as f:
        f.write(f"Correctness scores: {correctness_scores}\n")
        f.write(f"Faithfulness scores: {faithfulness_scores}\n")
        f.write(f"Relevancy scores: {relevancy_scores}\n")
    

if __name__ == "__main__":
    main()