import json

import faiss
import httpx
import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand
from openai import OpenAI

from core.models import Customer, Meal, Restaurant


class Command(BaseCommand):
    help = "Rebuild the FAISS RAG index and dataset directly from the database."

    def handle(self, *args, **options):
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            http_client=httpx.Client(verify=False),  # SSL workaround (dev only)
        )

        documents = []

        for rest in Restaurant.objects.all():
            documents.append(
                f"Restaurant: {rest.name} located at {rest.address} phone {rest.phone}."
            )

        for meal in Meal.objects.all():
            documents.append(
                f"Meal: {meal.name}. Description: {meal.description}. "
                f"Calories: {meal.calories}. Protein: {meal.protein}. "
                f"Carbs: {meal.carbs}. Fat: {meal.fat}."
            )

        for cust in Customer.objects.all():
            documents.append(
                f"Customer: {cust.name} age {cust.age} weight {cust.weight} "
                f"height {cust.height} goal is {cust.goal} likes {cust.likes} "
                f"dislikes {cust.dislikes} allergies {cust.allergies}."
            )

        self.stdout.write(f"Total documents: {len(documents)}")

        def embed(text):
            res = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return np.array(res.data[0].embedding, dtype="float32")

        self.stdout.write("Generating embeddings...")
        embeddings = np.array([embed(doc) for doc in documents], dtype="float32")

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        index_path = settings.BASE_DIR / "rag_index.faiss"
        dataset_path = settings.BASE_DIR / "rag_dataset.json"

        faiss.write_index(index, str(index_path))

        dataset = {
            "documents": documents,
            "embeddings": embeddings.tolist(),
        }

        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=4)

        self.stdout.write(self.style.SUCCESS(
            f"RAG index rebuilt successfully! Documents: {len(documents)}"
        ))
