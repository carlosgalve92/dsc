PL_SYSTEM_PROMPT = """
ROL:
Actúa como {rol}.

OBJETIVO:
{objetivo}

CONTEXTO:
{contexto}

RESTRICCIONES:
{restricciones}

CANALES:
{canales}

RAZONAMIENTO INTERNO:
{razonamiento}

FORMATO DE SALIDA:
{formato_salida}

EJEMPLOS DE REFERENCIA:
{ejemplos}
"""

PL_SUMMARIZE_PROMPT = """
ROL:
Actúa como {rol}.

OBJETIVO:
{objetivo}

CONTEXTO:
{contexto}

INFORMACIÓN A CONSERVAR:
{conservar}

RESTRICCIONES:
{restricciones}

FORMATO DE SALIDA:
{formato_salida}

EJEMPLO DE REFERENCIA:
{ejemplo}
"""