import ollama  # type: ignore

def get_response(prompt):
    MODEL_NAME = "llama3"
    context = "You are an AI assistant that helps users with their questions. Your name is 'Sign.Ai'. Your creators are Abhigyan and Medhansh. You implemented in the 'Sign Speak' prokect, its a ASL(american sign language) decoder."
    compiled_prompt = f"context: {context}\nUser: {prompt}"

    response = ollama.generate(MODEL_NAME, prompt=compiled_prompt)
    return response['response'] 
