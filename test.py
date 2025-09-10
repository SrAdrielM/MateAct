import numpy as np
import matplotlib.pyplot as plt
import io, base64
import scipy.integrate as spi
from sympy import symbols, integrate, sympify, lambdify

from reactpy import component, html, use_state
from reactpy.backend.starlette import configure
from starlette.applications import Starlette
import uvicorn

    # todo lo saque de chatgpt waza waza

# ---------------------------
# Función para calcular integral
# ---------------------------
def calcular_integral(funcion_str, a, b):
    x = symbols('x')
    funcion = sympify(funcion_str)

    # Integral simbólica
    integral_simbolica = integrate(funcion, (x, a, b))

    # Integral numérica
    f_num = lambdify(x, funcion, "numpy")
    resultado_numerico, error = spi.quad(f_num, a, b)

    # Gráfico con Matplotlib (convertido a base64 para mostrar en la web)
    X = np.linspace(a, b, 400)

    # 🔹 Asegurar que Y tenga la misma forma que X
    Y = np.array([f_num(val) for val in X], dtype=float)

    plt.figure()
    plt.plot(X, Y, label=f"f(x) = {funcion_str}")
    plt.fill_between(X, Y, alpha=0.3, color="skyblue", label="Área bajo la curva")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.legend()
    plt.title("Cálculo de integral")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")

    return integral_simbolica, resultado_numerico, error, img_base64


# ---------------------------
# Componente ReactPy
# ---------------------------
@component
def CalculadoraIntegral():
    funcion, set_funcion = use_state("")
    a, set_a = use_state("0")
    b, set_b = use_state("1")
    resultado, set_resultado = use_state("")
    grafico, set_grafico = use_state("")

    def handle_calcular(event):
        try:
            integral_sym, integral_num, error, img = calcular_integral(funcion, float(a), float(b))
            set_resultado(f"📘 Simbólica: {integral_sym} | 📐 Numérica: {integral_num:.6f}")
            set_grafico(img)
        except Exception as e:
            set_resultado(f"⚠️ Error: {e}")
            set_grafico("")

    return html.div(
        {
            "style": {"fontFamily": "Arial", "padding": "20px"}
        },
        html.h1("🧮 Calculadora de Integrales"),
        html.label("Función f(x): "),
        html.input({"value": funcion, "onChange": lambda e: set_funcion(e["target"]["value"])}),
        html.br(),
        html.label("Límite inferior (a): "),
        html.input({"value": a, "onChange": lambda e: set_a(e["target"]["value"])}),
        html.br(),
        html.label("Límite superior (b): "),
        html.input({"value": b, "onChange": lambda e: set_b(e["target"]["value"])}),
        html.br(),
        html.button({"onClick": handle_calcular}, "Calcular"),
        html.p(resultado),
        grafico and html.img({"src": f"data:image/png;base64,{grafico}", "style": {"maxWidth": "400px"}})
    )


# ---------------------------
# Configuración Starlette
# ---------------------------
app = Starlette(debug=True)
configure(app, CalculadoraIntegral)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
