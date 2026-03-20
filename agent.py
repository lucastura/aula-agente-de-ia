import ollama
import datetime

# 1. A nossa "Ferramenta" (Simulando uma ação física/sistema)
def obter_hora_atual():
    agora = datetime.datetime.now()
    return agora.strftime("%H:%M:%S")

# 2. Explicando a ferramenta para a IA (Schema)
ferramenta_hora = {
    'type': 'function',
    'function': {
        'name': 'obter_hora_atual',
        'description': 'Obtém a hora exata atual do relógio do sistema do computador.',
        'parameters': {
            'type': 'object',
            'properties': {},
            'required': []
        }
    }
}

print("🤖 Agente Qwen iniciado! Pergunte as horas. (Digite 'sair' para encerrar)\n")

# Histórico de mensagens: Damos um "norte" com o System Prompt
mensagens = [
    {'role': 'system', 'content': 'Você é um assistente prestativo focado em automação e robótica. Você é direto ao ponto, responde de forma amigável e sempre em português do Brasil.'}
]

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == 'sair':
        break

    # Adiciona a pergunta do usuário ao histórico
    mensagens.append({'role': 'user', 'content': pergunta})

    try:
        # 3. Primeira chamada: A IA avalia a pergunta e decide se usa a ferramenta
        resposta = ollama.chat(
            model='qwen2.5:3b',
            messages=mensagens,
            tools=[ferramenta_hora]
        )

        # Adicionamos a resposta inicial da IA (que contém a "intenção" de usar a ferramenta) ao histórico
        mensagens.append(resposta['message'])

        # 4. A mágica do Tool Calling: A IA pediu para usar a ferramenta?
        if resposta.get('message', {}).get('tool_calls'):
            for tool in resposta['message']['tool_calls']:
                if tool['function']['name'] == 'obter_hora_atual':
                    
                    # Executamos a nossa função Python real
                    hora_do_sistema = obter_hora_atual()
                    print(f"   [⚙️ Sistema: Função 'obter_hora_atual' executada. Resultado: {hora_do_sistema}]")
                    
                    # 5. Devolvemos o resultado da ferramenta para o histórico da IA
                    mensagens.append({
                        'role': 'tool',
                        'content': f"O relógio do sistema informou que agora são {hora_do_sistema}",
                        'name': 'obter_hora_atual'
                    })
                    
                    # 6. Segunda chamada: A IA lê o histórico atualizado com a hora e formula a resposta final
                    resposta_final = ollama.chat(
                        model='qwen2.5:3b',
                        messages=mensagens
                    )
                    
                    # Salva a resposta final no histórico para manter o contexto da conversa e imprime
                    mensagens.append(resposta_final['message'])
                    print(f"Agente: {resposta_final['message']['content']}\n")
        else:
            # Se não precisou de ferramenta (ex: "tudo bem?"), responde normalmente
            print(f"Agente: {resposta['message']['content']}\n")
            
    except Exception as e:
        print(f"Erro de conexão com o Ollama: {e}\n")