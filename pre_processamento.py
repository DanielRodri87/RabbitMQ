import os
import cv2

def convert_and_resize(input_folder, output_folder, size=(512, 512)):
    os.makedirs(output_folder, exist_ok=True)

    # Percorre todos os arquivos da pasta
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        # Pula se não for arquivo
        if not os.path.isfile(file_path):
            continue

        # Lê a imagem
        img = cv2.imread(file_path)
        if img is None:
            print(f"[ERRO] Não foi possível abrir: {filename}")
            continue

        # Redimensiona
        img_resized = cv2.resize(img, size, interpolation=cv2.INTER_AREA)

        # Define nome de saída (.png)
        base_name = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(output_folder, base_name)

        # Salva como PNG
        cv2.imwrite(output_path, img_resized)
        print(f"[OK] Convertido: {filename} -> {output_path}")

# Exemplo de uso:
if __name__ == "__main__":
    input_dir = "dataset-team/palmeiras"
    output_dir = "dataset-team/palmeiras"
    convert_and_resize(input_dir, output_dir)
