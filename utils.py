"""
Утилиты для AI-бота Шерлока Холмса
"""

import chromadb
from sentence_transformers import SentenceTransformer
import json
import time
from typing import List, Dict, Any

class SherlockUtils:
    def __init__(self):
        self.chroma_client = chromadb.Client()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        try:
            self.collection = self.chroma_client.get_collection("sherlock_knowledge")
        except:
            self.collection = self.chroma_client.create_collection(
                name="sherlock_knowledge",
                metadata={"hnsw:space": "cosine"}
            )

    def get_database_stats(self) -> Dict[str, Any]:
        """Получение статистики базы данных"""
        try:
            count = self.collection.count()
            
            # Получаем все метаданные для анализа
            results = self.collection.get()
            sources = {}
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    source = metadata.get('source', 'unknown')
                    if source in sources:
                        sources[source] += 1
                    else:
                        sources[source] = 1
            
            return {
                'total_records': count,
                'unique_sources': len(sources),
                'sources': sources
            }
        except Exception as e:
            return {'error': str(e)}

    def search_similar_content(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Поиск похожего контента"""
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            similar_content = []
            if results['documents'] and results['metadatas']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                    similar_content.append({
                        'content': doc,
                        'source': metadata.get('source', 'unknown'),
                        'title': metadata.get('title', ''),
                        'description': metadata.get('description', '')
                    })
            
            return similar_content
        except Exception as e:
            return [{'error': str(e)}]

    def export_database(self, filename: str = None) -> str:
        """Экспорт базы данных"""
        if not filename:
            filename = f"sherlock_database_{int(time.time())}.json"
        
        try:
            results = self.collection.get()
            
            export_data = {
                'export_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_records': len(results['documents']) if results['documents'] else 0,
                'records': []
            }
            
            if results['documents'] and results['metadatas']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if i < len(results['metadatas']) else {}
                    export_data['records'].append({
                        'content': doc,
                        'metadata': metadata,
                        'id': results['ids'][i] if i < len(results['ids']) else f"record_{i}"
                    })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return filename
        except Exception as e:
            raise Exception(f"Ошибка при экспорте: {e}")

    def import_database(self, filename: str) -> bool:
        """Импорт базы данных"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'records' not in import_data:
                raise Exception("Неверный формат файла")
            
            for record in import_data['records']:
                if 'content' in record and 'metadata' in record:
                    embedding = self.embedding_model.encode(record['content']).tolist()
                    
                    self.collection.add(
                        embeddings=[embedding],
                        documents=[record['content']],
                        metadatas=[record['metadata']],
                        ids=[record.get('id', f"imported_{int(time.time())}")]
                    )
            
            return True
        except Exception as e:
            raise Exception(f"Ошибка при импорте: {e}")

    def delete_source(self, source_url: str) -> bool:
        """Удаление всех записей из определенного источника"""
        try:
            results = self.collection.get()
            
            if not results['documents']:
                return True
            
            # Находим записи для удаления
            ids_to_delete = []
            if results['metadatas'] and results['ids']:
                for i, metadata in enumerate(results['metadatas']):
                    if metadata.get('source') == source_url:
                        ids_to_delete.append(results['ids'][i])
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
            
            return True
        except Exception as e:
            raise Exception(f"Ошибка при удалении источника: {e}")

    def get_source_info(self, source_url: str) -> Dict[str, Any]:
        """Получение информации об источнике"""
        try:
            results = self.collection.get()
            
            source_records = []
            if results['metadatas'] and results['documents']:
                for i, metadata in enumerate(results['metadatas']):
                    if metadata.get('source') == source_url:
                        source_records.append({
                            'content': results['documents'][i],
                            'metadata': metadata,
                            'id': results['ids'][i] if i < len(results['ids']) else f"record_{i}"
                        })
            
            return {
                'source_url': source_url,
                'record_count': len(source_records),
                'records': source_records
            }
        except Exception as e:
            return {'error': str(e)}

    def analyze_content(self, text: str) -> Dict[str, Any]:
        """Анализ текста"""
        try:
            # Простой анализ текста
            words = text.split()
            sentences = text.split('.')
            
            analysis = {
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'avg_sentence_length': len(words) / max(len([s for s in sentences if s.strip()]), 1),
                'unique_words': len(set(words)),
                'vocabulary_diversity': len(set(words)) / max(len(words), 1)
            }
            
            return analysis
        except Exception as e:
            return {'error': str(e)}

# Функции для работы с файлами
def save_conversation(messages: List[Dict[str, Any]], filename: str = None) -> str:
    """Сохранение диалога"""
    if not filename:
        filename = f"conversation_{int(time.time())}.json"
    
    conversation_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'messages': messages
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2)
    
    return filename

def load_conversation(filename: str) -> List[Dict[str, Any]]:
    """Загрузка диалога"""
    with open(filename, 'r', encoding='utf-8') as f:
        conversation_data = json.load(f)
    
    return conversation_data.get('messages', []) 