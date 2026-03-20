import tkinter as tk
from tkinter import scrolledtext
import threading
import ollama

# --- Configuração ---
MODELO = "qwen2.5:3b"

# --- Lógica da Interface ---
def atualizar_chat(texto, tag):
    """Insere o texto no chat com a cor e estilo corretos"""
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, texto + "\n\n", tag)
    chat_box.yview(tk.END) # Rola a tela para baixo
    chat_box.config(state=tk.DISABLED)

def processar_mensagem(pergunta):
    """Roda em background para não congelar a interface"""
    try:
        atualizar_chat("🤖 Processando...", "sistema_info")
        # =====================================================================
        # AULA: COMO A IA RECEBE A PERGUNTA NO MODO NORMAL
        # =====================================================================
        # Aqui a gente empacota a pergunta do usuário em um formato que a IA entende.
        # O formato é sempre um dicionário com quem está falando ('role') e o que foi dito ('content').
        # A IA recebe isso, processa as palavras estatisticamente e cospe o texto de volta.
        # Não há conexão com o mundo real, ela só "prevê" a próxima palavra.
        
        # Chamada simples para o Ollama (sem ferramentas, apenas chat normal)
        resposta = ollama.chat(
            model=MODELO,
            messages=[{'role': 'user', 'content': pergunta}]
        )
        # A resposta chega dentro de dicionários aninhados. A gente extrai só o texto final.
        texto_bot = resposta['message']['content']
        atualizar_chat(f"IA: {texto_bot}", "bot")
            
    except Exception as e:
        atualizar_chat(f"❌ Erro de conexão com o Ollama: {e}", "erro")

def enviar(event=None):
    texto_usuario = entrada.get()
    if not texto_usuario.strip(): return
    
    # Exibe a mensagem do usuário
    atualizar_chat(f"Você: {texto_usuario}", "usuario")
    entrada.delete(0, tk.END) # Limpa a caixa de texto
    
    # Inicia a thread de processamento
    threading.Thread(target=processar_mensagem, args=(texto_usuario,), daemon=True).start()

# --- Construção da Interface Gráfica (Dark Mode) ---
root = tk.Tk()
root.title("Terminal IA - Chat Base")
root.geometry("550x650")
root.configure(bg="#1E1E1E") # Fundo escuro

# Área do Chat
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, 
                                     bg="#1E1E1E", fg="#D4D4D4", 
                                     font=("Consolas", 11), bd=0, padx=10, pady=10)
chat_box.pack(fill=tk.BOTH, expand=True)

# Configuração de Cores (Tags)
chat_box.tag_config("usuario", foreground="#5CE1E6", font=("Consolas", 12, "bold")) # Ciano
chat_box.tag_config("bot", foreground="#FFFFFF", font=("Consolas", 12))             # Branco
chat_box.tag_config("sistema_info", foreground="#6c757d", font=("Consolas", 10))    # Cinza
chat_box.tag_config("erro", foreground="#FF4C4C", font=("Consolas", 11, "bold"))    # Vermelho

# Caixa de Entrada
frame_entrada = tk.Frame(root, bg="#1E1E1E", pady=10, padx=10)
frame_entrada.pack(fill=tk.X)

entrada = tk.Entry(frame_entrada, font=("Consolas", 12), bg="#2D2D2D", fg="white", 
                   insertbackground="white", relief=tk.FLAT)
entrada.pack(fill=tk.X, ipady=10)
entrada.bind("<Return>", enviar)

# Mensagem de inicialização
atualizar_chat(f"🟢 Sistema online. Chat Base carregado com o modelo {MODELO}.\nDigite sua mensagem abaixo.", "sistema_info")

root.mainloop()