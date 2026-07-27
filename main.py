from app.agent import consultar_agente


def main() -> None:
    pregunta = (
        "¿Cuánto tarda en llegar un pedido y "
        "qué métodos de pago aceptan?"
    )

    resultado = consultar_agente(pregunta)

    print("\n" + "=" * 80)
    print("RESPUESTA FINAL")
    print("=" * 80)
    print(resultado["output"])

    print("\n" + "=" * 80)
    print("HERRAMIENTAS UTILIZADAS")
    print("=" * 80)

    pasos = resultado["intermediate_steps"]

    if not pasos:
        print("No fue necesario consultar herramientas.")
        return

    for paso in pasos:
        print("Herramienta:", paso["tool"])
        print("Entrada:", paso["tool_input"])

        if paso["error"]:
            print("Estado: error")
        else:
            print("Estado: correcto")

        print("\nResultado recuperado:")
        print(paso["output"])
        print("-" * 80)


if __name__ == "__main__":
    main()