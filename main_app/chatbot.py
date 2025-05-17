from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from huggingface_hub import login
import torch
import os

# Убедитесь, что токен действительный и имеет доступ к модели
login(token="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")


class PrinterAssistantBot:
    def __init__(self, model_name="deepseek-ai/deepseek-coder-1.3b-instruct"):
        try:
            # Конфигурация для квантования (если доступен CUDA)
            quantization_config = None
            if torch.cuda.is_available():
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16
                )

            # Загрузка токенизатора
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            # Загрузка модели с учетом доступности GPU
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
                quantization_config=quantization_config,
                use_safetensors=True
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Переводим модель в режим оценки для ускорения
            self.model.eval()

            print(f"Модель {model_name} успешно загружена!")
            print(f"Используется устройство: {self.model.device}")

        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            raise

    def respond(self, user_input, max_length=200):
        try:
            # Промпт для технического ассистента
            prompt = f"""Ты - консультант магазина принтеров. Отвечай кратко и технически точно.
            Вопрос: {user_input}
            Ответ:"""

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.model.device)

            # Быстрая генерация
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    do_sample=True,
                    temperature=0.7,
                    top_k=40,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )

            return response[:500]  # Обрезаем слишком длинные ответы

        except Exception as e:
            return f"Ошибка: {str(e)}"


def main():
    print("Загрузка модели DeepSeek-Coder...")
    try:
        bot = PrinterAssistantBot()
        # print("Готов к работе! Задавайте вопросы о принтерах (для выхода введите 'выход').")
        response = bot.respond(user_input)  # ТУТ ОТВЕТ
        # print(f"Ассистент: {response}")

    except Exception as e:
        print(f"Фатальная ошибка: {e}")


if __name__ == "__main__":
    main()
