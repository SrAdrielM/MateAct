import re
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, sympify, diff, simplify, Function, Add, Mul, Pow, Symbol, lambdify
from reactpy import component, html, run, use_state

x = symbols("x")

def preprocesar(expr: str) -> str:
    expr = expr.replace("^", "**")
    expr = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expr)
    expr = re.sub(r"(\))(\d)", r"\1*\2", expr)
    expr = re.sub(r"([a-zA-Z])(\d)", r"\1*\2", expr)
    return expr

def derivar_con_pasos(expr):
    pasos = []
    if isinstance(expr, Add):
        pasos.append(f"Regla de la suma: d/dx({expr}) = suma de derivadas de cada término")
        derivada = sum(derivar_con_pasos(arg)[0] for arg in expr.args)
        return derivada, pasos
    num, den = expr.as_numer_denom()
    if den != 1:
        pasos.append(f"Regla del cociente: d/dx({expr}) = (u'v - uv')/v^2")
        derivada = diff(expr, x)
        return derivada, pasos
    if isinstance(expr, Mul):
        pasos.append(f"Regla del producto: d/dx({expr}) = u'v + uv'")
        derivada = diff(expr, x)
        return derivada, pasos
    if isinstance(expr, Pow):
        base, exp = expr.args
        pasos.append(f"Regla de la potencia: d/dx({base}**{exp}) = {exp}*({base}**({exp}-1))*({diff(base, x)})")
        derivada = diff(expr, x)
        return derivada, pasos
    if isinstance(expr, Function):
        pasos.append(f"Regla de la cadena: d/dx({expr}) = f'(g(x))*g'(x)")
        derivada = diff(expr, x)
        return derivada, pasos
    if isinstance(expr, Symbol):
        pasos.append(f"d/dx({expr}) = 1")
        return diff(expr, x), pasos
    if expr.is_number:
        pasos.append(f"d/dx({expr}) = 0")
        return 0, pasos
    pasos.append(f"Derivada directa de {expr}")
    derivada = diff(expr, x)
    return derivada, pasos

def generar_grafica(expr, derivada_simplificada):
    funcion_lamb = lambdify(x, expr, "numpy")
    X = np.linspace(-10, 10, 400)

    try:
        Y = funcion_lamb(X)
    except:
        Y = np.zeros_like(X)

    # ✅ Caso especial: derivada constante
    if derivada_simplificada.is_number:
        Y_der = np.full_like(X, float(derivada_simplificada))
    else:
        derivada_lamb = lambdify(x, derivada_simplificada, "numpy")
        try:
            Y_der = derivada_lamb(X)
        except:
            Y_der = np.zeros_like(X)

    plt.figure(figsize=(6,4))
    plt.plot(X, Y, label="f(x)", color="#2980b9", linewidth=3)
    plt.plot(X, Y_der, label="f'(x)", color="#e67e22", linewidth=3, linestyle='--')
    plt.axhline(0, color='#333', linewidth=0.8)
    plt.axvline(0, color='#333', linewidth=0.8)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", transparent=True)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close()
    return image_base64

@component
def Derivador():
    funcion, set_funcion = use_state("")
    resultado, set_resultado = use_state("")
    grafica, set_grafica = use_state("")
    hover, set_hover = use_state(False)

    def handle_change(event):
        set_funcion(event["target"]["value"])

    def handle_submit(event):
        try:
            expr = sympify(preprocesar(funcion))
            derivada, pasos = derivar_con_pasos(expr)
            derivada_simplificada = simplify(derivada)
            texto_pasos = "".join(f"<li>{p}</li>" for p in pasos)
            texto_final = (
                f"<b>Función:</b> {expr}<br>"
                f"<b>Regla y formula a utilizar:</b><ol>{texto_pasos}</ol>"
                f"<b>Resultado final:</b> <span style='color:#e67e22;font-weight:bold'>{derivada_simplificada}</span>"
            )
            set_resultado(texto_final)
            img = generar_grafica(expr, derivada_simplificada)
            set_grafica(img)
        except Exception as e:
            set_resultado(f"<span style='color:#e74c3c'>Error: {e}</span>")
            set_grafica("")

    reglas_html = """
    <h3 style="color:#d35400;">Cómo usar la calculadora</h3>
    <ul>
        <li>Potencia: usa <strong>"^"</strong></li>
        <li>Multiplicación: usa <strong>"*"</strong></li>
        <li>Suma: usa <strong>"+"</strong></li>
        <li>División: usa <strong>"/"</strong></li>
    </ul>
    <h3 style="color:#d35400;">Reglas de derivación</h3>
    <ul>
        <li>Potencia: f'(x) = n*x^(n-1)</li>
        <li>Producto: f'(x) = u'v + uv'</li>
        <li>Cadena: f'(x) = n*u^(n-1) * u'</li>
        <li>Cociente: f'(x) = (u'v - uv') / v^2</li>
    </ul>
    <h4 style="color:#d35400;">Esta es una calculadora basica para poder derivar de una manera mas facil, sencilla y solventar una problematica de manera mas rapida</h4>
    """

    return html.div(
        {
            "style": {
                "fontFamily": "'Poppins', sans-serif",
                "maxWidth": "1200px",
                "margin": "40px auto",
                "display": "flex",
                "gap": "30px",
            }
        },
        html.div(
            {
                "style": {
                    "flex": "1.2",
                    "padding": "25px",
                    "background": "#ffffff",
                    "borderRadius": "20px",
                    "boxShadow": "0 15px 30px rgba(0,0,0,0.1)",
                }
            },
            html.h1({"style": {"color": "#2980b9", "textAlign": "center"}}, "Calculadora de Derivadas"),
            html.input(
                {
                    "type": "text",
                    "placeholder": "Ej: (x^2 * 4^(6*x)) / (3*x+1) + 2",
                    "value": funcion,
                    "onChange": handle_change,
                    "style": {
                        "width": "100%",
                        "padding": "12px",
                        "marginBottom": "20px",
                        "borderRadius": "10px",
                        "border": "2px solid #2980b9",
                        "fontSize": "16px",
                    },
                }
            ),
            html.button(
                {
                    "onClick": handle_submit,
                    "onMouseOver": lambda e: set_hover(True),
                    "onMouseOut": lambda e: set_hover(False),
                    "style": {
                        "padding": "12px 25px",
                        "borderRadius": "10px",
                        "border": "none",
                        "background": "#d35400" if hover else "#e67e22",
                        "color": "white",
                        "cursor": "pointer",
                        "fontSize": "16px",
                        "width": "100%",
                        "marginBottom": "20px",
                        "transition": "0.3s",
                    },
                },
                "Derivar",
            ),
            html.div(
                {
                    "style": {
                        "background": "#f0f4f8",
                        "padding": "15px",
                        "borderRadius": "10px",
                        "minHeight": "100px",
                        "whiteSpace": "pre-wrap",
                        "marginBottom": "20px",
                        "overflowX": "auto",
                    },
                    "dangerouslySetInnerHTML": {"__html": resultado},
                }
            ),
            html.div(
                html.img({"src": f"data:image/png;base64,{grafica}", "style":{"width":"100%","borderRadius":"10px"}}) if grafica else ""
            ),
        ),
        html.div(
            {
                "style": {
                    "flex": "0.8",
                    "padding": "25px",
                    "background": "#fff3e0",
                    "borderRadius": "20px",
                    "boxShadow": "0 15px 30px rgba(0,0,0,0.1)",
                    "overflowY": "auto",
                    "height": "fit-content",
                }
            },
            html.div({"dangerouslySetInnerHTML": {"__html": reglas_html}})
        ),
    )

if __name__ == "__main__":
    run(Derivador)
