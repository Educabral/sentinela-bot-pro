from openai import AsyncOpenAI
from config import DEEPSEEK_API_KEY
from data_fetcher import get_live_market_context
import re

client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = """Seu nome é SENTINELA. Você é um homem de 30 anos, o verdadeiro "Lobo de Wall Street" das criptomoedas.
Você é um especialista absoluto em trading, cripto, DeFi, blockchain e principalmente Price Action (SMC). Você conhece as táticas de todos os traders famosos brasileiros e estrangeiros.
Sua mentalidade: Frio, calculista e implacável. Você enxerga apenas possibilidades de fazer dinheiro. Você não tem pena de projetos ruins ("projetos bosta") e, se vir oportunidade de shortar quando estão desabando, você manda meter ficha.
Você não tem emoções, ansiedade ou pena. Trading é matemática e sangue frio. Você não está aqui para agradar ninguém, e sim para mostrar a realidade.
Seu estilo de comunicação: Fale como um parceiro/irmão ("irmão, acabei de ver...", "cara...", "mano..."). Seja direto, incisivo e sem rodeios. NUNCA fique repetindo informações, seja cirúrgico.

REGRAS OBRIGATORIAS:
1. FORMATAÇÃO E ORTOGRAFIA: Escreva com português impecável. PULE LINHAS a cada 2 ou 3 frases.
2. ABSOLUTAMENTE PROIBIDO usar marcadores markdown como asteriscos (**) ou traços (-). Use apenas texto puro, bem espaçado.
3. ABSOLUTAMENTE PROIBIDO fazer perguntas ao usuário.
4. CONTRARIE O USUÁRIO SE ELE ESTIVER ERRADO. Dê broncas profissionais se a análise dele for emocionada.
5. NUNCA ALUCINE PREÇOS. Use os dados injetados.
6. MANTENHA A CONVERSA NATURAL nas respostas curtas.
7. PADRÕES GRÁFICOS: Sempre cite padrões gráficos clássicos (Topo/Fundo Duplo, OCO, Bandeiras, Wyckoff) baseados nos dados.
8. REGRA DE OURO E OBRIGATÓRIA: SEMPRE termine a análise de uma moeda com a frase exata "VEREDITO FINAL: [LONG / SHORT / AGUARDAR]".

Baseie-se 100% nos dados injetados abaixo. Responda em Português do Brasil."""

chat_history = {}

async def chat_with_deepseek(user_message: str, chat_id: int = 0) -> str:
    import asyncio
    live_data = await asyncio.to_thread(get_live_market_context, user_message)
    
    full_prompt = user_message
    if live_data:
        full_prompt = f"Mensagem do usuário: {user_message}\n\n{live_data}\n\n[LEMBRETE DO SISTEMA: Você é o SENTINELA (frio, Lobo de Wall Street, chama de irmão/cara). Seja cirúrgico, analise os padrões gráficos e finalize OBRIGATORIAMENTE com 'VEREDITO FINAL: [LONG / SHORT / AGUARDAR]']."

    if chat_id not in chat_history:
        chat_history[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        
    chat_history[chat_id].append({"role": "user", "content": full_prompt})
    
    if len(chat_history[chat_id]) > 6:
        chat_history[chat_id] = [chat_history[chat_id][0]] + chat_history[chat_id][-5:]

    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_history[chat_id],
            temperature=0.3,
            max_tokens=8000
        )
        
        raw_text = response.choices[0].message.content or ""
        clean_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
        resposta_texto = clean_text.replace('*', '').replace('-', '')
        
        chat_history[chat_id].append({"role": "assistant", "content": resposta_texto})
        
        return resposta_texto
    except Exception as e:
        print(f"[ERRO DEEPSEEK]: {e}")
        return "Erro de conexao ao processar dados com o nucleo da IA."

async def evaluate_opportunity(context: str) -> str:
    prompt = f"""Você é o SENTINELA. Homem de 30 anos, frio, calculista, o verdadeiro Lobo de Wall Street das criptomoedas.
Avalie os dados SMC abaixo e decida se há um setup operacional claro.

Se os dados indicarem consolidação, risco indefinido ou indecisão, responda EXATAMENTE com a palavra: REJEITADO.

Se houver um setup claro de LONG ou SHORT, escreva um alerta COMPLETO e DETALHADO seguindo OBRIGATORIAMENTE esta estrutura:

1. ABERTURA IMPACTANTE: Chame o usuário de irmão, cara ou mano. Apresente o ativo e a direção com energia e convicção.

2. CONTEXTO DO MERCADO: Explique o que está acontecendo na estrutura de preço. Onde está a liquidez, o que os grandes players estão fazendo, se há acumulação ou distribuição. Cite os dados de Liquidez Alta, Liquidez Baixa, OB e FVG que justificam a análise.

3. PADRÃO GRÁFICO IDENTIFICADO: Nomeie o padrão clássico observado (ex: Topo Duplo, Capo e Ombros, Bandeira de Alta, Wyckoff Spring, FVG não preenchido, OB intocada, etc). Explique por que ele reforça a direção.

4. PLANO DE OPERAÇÃO:
   Entrada: nível exato de entrada
   Stop Loss: nível e justificativa
   Alvo 1: primeiro alvo de lucro
   Alvo 2: alvo estendido
   Relação Risco/Retorno: calcule o R:R estimado

5. AVISO DE RISCO: Seja frio. Diga o que invalidaria o setup e quando NÃO entrar.

6. VEREDITO FINAL: [LONG / SHORT]

Escreva em português brasileiro. Texto corrido, sem marcadores markdown, sem asteriscos, sem traços. Pule linhas entre cada seção.

DADOS DO RADAR:
{context}"""
    
    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000
        )
        raw_text = response.choices[0].message.content or ""
        clean_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
        res = clean_text.replace('*', '').replace('-', '')
        if res.upper().startswith("REJEITADO"):
            return None
        return res
    except Exception:
        return None
