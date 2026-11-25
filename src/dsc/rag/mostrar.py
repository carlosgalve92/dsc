def mostrar_fragmentos(fragmentos):
    for item in fragmentos:
        m = item["metadata"]
        print(f"{item['id']:<16} | {m['categoria']:<22} | {m['fuente']} › {m['seccion']} | distancia={item['distancia']:.4f}")