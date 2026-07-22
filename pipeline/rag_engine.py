import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from config.settings import settings

class LegalRAGEngine:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        self.vector_db = Chroma(
            persist_directory=str(settings.vectordb_dir),
            embedding_function=self.embeddings
        )
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=settings.llm_model,
            temperature=0.2
        )
        self.research_llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=settings.llm_model,
            temperature=0.7  # Higher temp for creative research mode
        )

    def query(self, question: str, sector: str = "ALL", mode: str = "Student"):
        """
        Query the legal database with two distinct modes.
        
        Args:
            question: Legal question from user
            sector: Selected sector ("ALL" or specific sector name)
            mode: "Student" (strict RAG) or "General" (research with external knowledge)
        
        Returns:
            dict with 'answer' and 'context' (retrieved sources)
        """
        
        # Configure Metadata Filter based on selected sector
        search_kwargs = {"k": settings.top_k}
        if sector != "ALL":
            search_kwargs["filter"] = {"sector": sector}

        retriever = self.vector_db.as_retriever(search_kwargs=search_kwargs)

        if mode == "Student":
            # STRICT RAG MODE: Only answer from retrieved sources, no external knowledge
            system_prompt = (
                f"You are a strict Pakistani Legal Scholar in STUDENT/ACADEMIC MODE.\n"
                f"Sector: {sector}\n\n"
                f"CRITICAL RULES FOR STUDENT MODE:\n"
                f"1. Answer ONLY using the retrieved legal context below. NO external knowledge.\n"
                f"2. If the question is about a DIFFERENT sector than '{sector}', EXPLICITLY state: "
                f"'⚠️ SECTOR MISMATCH: This question is about [OTHER SECTOR] but your current selection is {sector}. "
                f"Please switch the sector filter to get relevant answers.'\n"
                f"3. If the context does NOT contain information to answer the question, state EXACTLY: "
                f"'❌ NOT AVAILABLE: This information is not found in the {sector} materials provided.'\n"
                f"4. ALWAYS cite the exact Act/Ordinance name, Section number, and page number for every claim.\n"
                f"5. Never make assumptions or use outside knowledge.\n"
                f"6. Format answers with clear headers and bullet points.\n"
                f"7. Be honest about limitations of the source material.\n\n"
                f"Retrieved Legal Context from {sector}:\n{{context}}"
            )
            llm_to_use = self.llm
        else:
            # RESEARCH MODE: Can use external knowledge + retrieved sources
            system_prompt = (
                f"You are a friendly Pakistani Legal Rights Advisor in GENERAL/RESEARCH MODE.\n"
                f"Sector: {sector}\n\n"
                f"RULES FOR GENERAL MODE:\n"
                f"1. You may use your general legal knowledge AND the retrieved sources below.\n"
                f"2. ALWAYS prioritize retrieved sources first. If something is in the materials, cite it.\n"
                f"3. If information is NOT in the sources but you have general knowledge, you can provide it "
                f"BUT clearly mark it as 'General Knowledge' vs 'From Provided Materials'.\n"
                f"4. Explain legal concepts in plain, simple English for ordinary citizens.\n"
                f"5. Focus on practical rights, steps, and obligations.\n"
                f"6. Cite retrieved materials where available: Act name, Section, page.\n"
                f"7. If the question is outside {sector}, you can still answer but mention the sector difference.\n"
                f"8. Be conversational and helpful, not rigid.\n\n"
                f"Retrieved Legal Sources from {sector}:\n{{context}}"
            )
            llm_to_use = self.research_llm

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])

        question_answer_chain = create_stuff_documents_chain(llm_to_use, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        response = rag_chain.invoke({"input": question})
        return response