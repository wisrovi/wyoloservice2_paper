\raggedbottom

# Generación de Informes de Entrenamiento Asistida por LLM en un Pipeline MLOps Distribuido: Arquitectura, Respaldo Determinista y Evaluación Empírica
**Author:** William Steve Rodriguez Villamizar (wisrovi rodriguez)\\AI Leader \& Solutions Architect\\wisrovi-suit (https://github.com/wisrovi/w-cli)

## Resumen y Palabras Clave
**Resumen:** Cada entrenamiento YOLO en el clúster NeuralForgeAI deja curvas de pérdida, matrices de confusión e informes JSON forenses; interpretarlos a mano no escala con las búsquedas de Optuna que generan cientos de ensayos. Documentamos `LlmAnalyzer`, paso final de un pipeline de 15 pasos que convierte `results.csv` y los JSON forenses en un informe Markdown y un DOCX con marca corporativa mediante un LLM local servido por OpenCode; un respaldo determinista garantiza un informe válido si la llamada falla. Medimos tal respaldo: mediana de 0.03\,ms en 120 ejecuciones sobre seis archivos (tres conjuntos de datos únicos), y recuperación de una caída simulada del LLM en 0.12\,ms. La vía LLM tardó 8.0--13.8\,s (mediana 12.4\,s), éxito 3/3, y señaló por sí sola una anomalía real de precisión--recall. Siete de los catorce estados forenses son andamiaje que emite valores analíticos deterministas en lugar de muestras aleatorias; declaramos esta limitación explícitamente y no reportamos sus salidas como medidas experimentales. El pipeline se publica bajo una Licencia Dual (PolyForm / AGPLv3) mediante el repositorio `wyoloservice2\_production`.

**Palabras clave:** Modelos de Lenguaje Grande, Generación Automatizada de Informes, MLOps, WPipe, Respaldo Determinista, Control de Alucinaciones, Visión por Computadora.

## Información del Autor
Esta investigación fue concebida y desarrollada por William Steve Rodriguez Villamizar (wisrovi rodriguez), AI Leader \& Solutions Architect del ecosistema wisrovi-suit (https://github.com/wisrovi/w-cli). Contacto: wisrovi.rodriguez@gmail.com.

## Introducción
Una sola ejecución de entrenamiento produce más artefactos de los que un investigador puede leer. `professional\_post\_train\_pipeline` ejecuta 15 pasos de WPipe: limpia el workspace, re-evalúa el modelo, genera mapas de calor Grad-CAM y ejecuta evaluadores de robustez, ataques adversarios, incertidumbre y complejidad computacional. Cada uno escribe un JSON en `extras/`; un estudio de hiperparámetros lo multiplica por cientos de ensayos. Nadie lee la salida.

Atacamos el cuello de botella en el punto de consumo. Un LLM local al final del pipeline lee los artefactos y escribe un informe ejecutivo. El diseño es deliberadamente simple: un paso, un prompt, un tiempo límite estricto, un respaldo determinista. La ingeniería interesante está en dónde se ejecuta: un clúster de Celery con nodos GPU efímeros en Docker, donde una llamada al LLM que falla no debe bloquear una cola y donde enviar métricas a una API pública no es aceptable.

Aportamos tres contribuciones: la descripción precisa de un paso de generación de informes con LLM en producción y su cadena de fallos; una evaluación empírica honesta con latencias y tasas de éxito reales de ambas vías, más una ablación de los modos de fallo; y una formulación determinista de todos los estados forenses para asegurar que el pipeline LLM se evalúe sobre modelos matemáticos fundamentados en lugar de ruido estocástico.

## Trabajo Relacionado
La generación temprana de informes se basaba en plantillas y modelos seq2seq, demostrada en imagen médica, donde los informes son cortos y estructurados . Esos modelos deben entrenarse por dominio y no se adaptan a un esquema que cambia en cada sprint. Los LLM preentrenados cambiaron la economía: el prompting zero-shot interpreta entradas estructuradas arbitrarias sin fine-tuning , y los agentes que usan herramientas, como Toolformer y ReAct, los extendieron a APIs y acciones .

Aplicar LLM a la escritura profesional es un campo activo. Van Veen et al. mostraron que los LLM adaptados igualan o superan a expertos médicos en la síntesis de textos clínicos, pero su análisis de seguridad expuso información fabricada . Eso enmarca nuestro problema: el valor de un informe LLM depende de detectar cuándo el modelo inventa datos. HaluEval mide la alucinación en la generación  y TruthfulQA sondea las falsedades afirmadas con confianza , pero ninguna aborda nuestro caso operativo: un LLM que escribe desde métricas estructuradas cuya verdad de referencia está en el mismo archivo que leyó.

Los tipos de métricas que interpreta el pipeline provienen de evaluadores consolidados. Grad-CAM localiza las regiones que usa un modelo ; el Método de Signo de Gradiente Rápido sondea la vulnerabilidad adversaria ; MC-Dropout estima la incertidumbre epistémica ; la Distancia Inception de Fr\'echet puntúa el cambio de dominio ; ImageNet-C define la robustez ante corrupciones ; t-SNE visualiza el espacio latente ; el costo de hardware reporta FLOPs más latencia medida . MLflow estableció el tracking como servicio de plataforma ; nuestro paso cierra el ciclo de métricas a narrativa.

La brecha es de integración, no de diseño de algoritmos. La investigación en generación de informes valida la calidad con paneles humanos fuera de línea ; los sistemas MLOps registran métricas pero no las narran. Nuestro paso se ubica en el medio: pipeline en vivo, latencia acotada, ejecución local y un respaldo que hace opcional al LLM.

## Arquitectura Propuesta / Metodología
### Ubicación en el Pipeline
`LlmAnalyzer` se registra como paso de WPipe (`@step(name="llm\_analyzer", version="v1.0")`) y se adjunta como último elemento de `professional\_post\_train\_pipeline` (`post\_train\_pipeline.py:67`). La Figura~ muestra los 15 pasos. El pipeline corre dentro del contenedor ejecutor efímero tras el entrenamiento y la evaluación, así que el informe se escribe en el mismo directorio de artefactos que el invocador recoge y archiva.

### Los Dos Canales de Salida
El paso produce dos artefactos desde dos entradas distintas, distinción que la versión anterior de este artículo difuminaba. Primero, `\_explain\_research\_states` recorre `extras/*/*.json`, pide al modelo que ``analyze all these data in a joint manner,'' y escribe un informe ejecutivo `GLOBAL\_RESEARCH\_EXPLANATION.md` (tiempo límite de 300\,s). Segundo, la vía principal lee `evaluation\_metrics/results.csv` mediante `TrainingReportAnalyzer.analyze()`, produciendo `extras/llm/LLM\_Report.md` y compilando `extras/llm/LLM\_Report.docx` con python-docx e imágenes de marca corporativa. El DOCX deriva de `results.csv`, no de `GLOBAL\_RESEARCH\_EXPLANATION.md`; los canales responden preguntas distintas en el mismo paso.

### La Cadena de Respaldo
`TrainingReportAnalyzer` implementa una cadena de tres etapas:

    - Intentar OpenCode: `opencode run --model opencode/deepseek-v4-flash-free` con un prompt fijo (tres secciones, máximo tres líneas cada una, ``Do not invent data'') y un tiempo límite de 180\,s. Una salida de menos de 50 caracteres se trata como fallo.
    - Ante cualquier excepción o salida vacía, `\_generate\_fallback\_report`: un analizador en Python puro que lee la última fila de `results.csv`, extrae pérdida de entrenamiento/validación, precisión, recall, mAP@50, mAP@50--95 y accuracy, y calcula un indicador de riesgo de sobreajuste por heurística (alto si la pérdida de entrenamiento bajó mientras la de validación subió; medio si la pérdida de validación creció más del 20\% sobre su primer valor).
    - Si el CSV no es legible, emitir un mensaje degradado fijo que apunte al archivo de métricas.

La cadena siempre devuelve una cadena. La entrada faltante falla rápido: un `results.csv` ausente lanza `FileNotFoundError`, que `LlmAnalyzer` convierte en un informe vacío y una cadena de error, mientras `safe\_step` mantiene el pipeline vivo. El modelo corre por el binario local (`/root/.opencode/bin/opencode`); ninguna métrica sale del clúster---coherente con la política shift-left---al precio de mayor varianza y una latencia de peor caso limitada por los tiempos de 180\,s y 300\,s.

## Configuración Experimental y Detalles de Implementación
### Estados Forenses Deterministas
El pipeline es real y está completamente integrado. Sin embargo, siete de los catorce estados forenses emiten valores analíticos deterministas (ej., degradación exponencial, proxy de oclusión sobre imagen sintética, medias FID fijas) en lugar de muestras aleatorias; `model_complexity_profiler` mide GFLOPs/parámetros/latencia reales. Declaramos esta limitación explícitamente y no afirmamos que estos siete estados deriven de salidas reales del modelo.

### Mediciones Reales
La superficie evaluable es el canal de informes. Ejecutamos el `TrainingReportAnalyzer` de producción sin cambios sobre seis archivos (tres conjuntos de datos únicos) del repositorio (dos de detección, dos de clasificación y dos de segmentación, con métricas reales por época); para la vía LLM usamos el mismo binario y modelo de OpenCode que el contenedor del trabajador. El host fue una estación RTX 3060 (12\,GB), Intel Core i7-9700F, 32\,GB de RAM---el mismo modelo de GPU que el trabajador. El cronometraje usó `time.perf\_counter()`.

### Infraestructura
El clúster es un despliegue privado local (on-premise) de pequeña escala. El host de control corre Redis y el broker de Celery; la configuración del trabajador limita el pool a `MAX\_GPU=30`, y el trabajador documentado es un único host físico con una RTX 3060 (12\,GB), 24\,GB de RAM y 7 núcleos de CPU.

## Resultados y Discusión
### Generación de Informes con LLM
La Tabla~ reporta la vía LLM sobre tres artefactos reales. El modelo devolvió un informe válido de tres secciones en todos los casos, con mediana de 12.4\,s. La dispersión es amplia (7.96--13.80\,s), esperable en un modelo alojado de nivel gratuito y la razón de que el pipeline use un tiempo límite en vez de un presupuesto fijo. La versión anterior de este artículo afirmaba un promedio de 42\,s; no pudimos reproducir esa cifra.

### Respaldo Determinista
La Tabla~ agrega 120 ejecuciones del respaldo (20 ensayos por cada uno de los seis archivos (tres conjuntos de datos únicos)). La vía determinista es casi gratis: mediana de 0.030\,ms, percentil 99 de 0.070\,ms, intervalo de confianza bootstrap del 95\% para la media [0.031, 0.034]\,ms. Devolvió un informe válido de tres secciones en cada artefacto.

### Valor Cualitativo de la Vía LLM
El costo de la vía LLM supera al respaldo en tres órdenes de magnitud, así que debe justificar su precio con afirmaciones fundamentadas en los números que leyó. En el artefacto de detección, el CSV contiene precisión 0.00485 y recall 1.0. El LLM concluyó que este desequilibrio extremo de precisión--recall revela ``a significant calibration or prediction-threshold problem'' y que el despliegue ``must be postponed until these anomalies are resolved.'' El respaldo imprime los mismos números con una etiqueta de sobreajuste y se detiene. La contribución del LLM es la interpretación, verificable contra el archivo que recibió el modelo---el marco de HaluEval y TruthfulQA : el archivo de métricas es la verdad de referencia, y una afirmación que la contradiga es una alucinación detectable. No hemos automatizado esa comprobación; es una limitación declarada.

## Estudio de Ablación
Ablamos la cadena de informes a lo largo de tres ejes (Tabla~).

**Solo LLM.** Sin el respaldo, una caída o una respuesta malformada dejan sin informe; el guardián de salida corta (\textless{}50 caracteres) convierte una finalización basura en fallo: una página en blanco es mejor que una fabricada. **Solo respaldo.** El analizador determinista nunca falló en 120 ejecuciones. **LLM + respaldo.** Con una caída inyectada en la llamada a OpenCode, la cadena produjo un informe válido en 0.123\,ms. **Sin `\_explain\_research\_states**.` Quitar ese canal solo elimina `GLOBAL\_RESEARCH\_EXPLANATION.md`; `LLM\_Report.md` y el DOCX vienen de `results.csv` y siguen disponibles. **Entrada faltante.** Un `results.csv` ausente se convierte en un informe vacío y una cadena de error, y `safe\_step` mantiene el pipeline corriendo.

Omitimos un estudio con línea base humana: comparar el LLM contra informes humanos exige un panel de lectores y una rúbrica, y la evidencia de la Sección~7.3 es de una sola ejecución; es la principal amenaza a la validez externa.

## Declaración de Disponibilidad de Datos y Código
El sistema es de código abierto bajo una Licencia Dual (PolyForm Noncommercial / AGPLv3). Para desplegar y reproducir el pipeline, use https://github.com/wisrovi/wyoloservice2_production y ejecute `docker-compose up -d`. El paso de informes vive en `wyoloservice2\_worker/executor\_v2.0/wtrain/lib/src/wyolo/trainer/states/llm\_analyzer.py` y `utils/training\_report\_analyzer.py`; los seis archivos (tres conjuntos de datos únicos) viajan en el repositorio, así que los números del respaldo se reproducen fuera de línea sin GPU. Los números del LLM dependen de la disponibilidad de `opencode/deepseek-v4-flash-free` en tiempo de ejecución.

## Impacto Más Amplio / Declaración Ética
La inferencia local elimina el costo de carbono y de privacidad de las APIs alojadas. La preocupación de doble uso es el reverso de la utilidad: un modelo que escribe informes plausibles con confianza también puede escribir fabricaciones plausibles que se archivan. Mitigamos con la instrucción ``Do not invent data'', el guardián de rechazo por salida corta y un respaldo que degrada a números crudos. Ninguno es una garantía. La generación de informes es confiable solo mientras las métricas de origen sigan inspeccionables junto a la narrativa; por eso ambos archivos se archivan juntos. Automatizar la verificación de alucinaciones es una prioridad de investigación, no un problema resuelto.

## Conclusión y Trabajo Futuro
Documentamos un paso de generación de informes con LLM en producción, acotamos sus fallos con un respaldo determinista y medimos ambas vías con datos reales: el respaldo a 0.03\,ms con 100\% de disponibilidad, el LLM a una mediana de 12.4\,s con salida fundamentada. La arquitectura no es una novedad teórica; su valor es operativo. Trabajo futuro: automatizar la verificación de alucinaciones contrastando cada afirmación numérica con los archivos de métricas; y escalar la evaluación del LLM con un panel de lectores humanos frente a una línea base de plantilla.

## Agradecimientos
Agradecemos a los contribuyentes de wisrovi-suit por la infraestructura de CLI y pipeline, y a las entidades que respaldan el clúster NeuralForgeAI.