# 🐄 Bovine Weight Calculation by Mask R-CNN (Keras & TensorFlow)

Este projeto implementa uma solução baseada em **Redes Neurais Convolucionais (Mask R-CNN)** para **segmentação de imagens de bovinos** e cálculo de métricas morfométricas (área, perímetro, largura, comprimento), possibilitando a **predição do peso** a partir de imagens.

---

## 📌 Funcionalidades
- Treinamento de um modelo **Mask R-CNN** em dataset customizado.  
- Segmentação automática de bovinos em imagens.  
- Cálculo de:
  - Área (px e cm²)  
  - Perímetro (px e cm)  
  - Comprimento e largura (px e cm)  
- Predição de peso com base na área segmentada.  
- Exportação dos resultados em **Excel (.xlsx)**.  

---

## 🛠️ Tecnologias Utilizadas
- [Python 3](https://www.python.org/)  
- [TensorFlow 2.5](https://www.tensorflow.org/)  
- [Keras](https://keras.io/)  
- [Mask R-CNN](https://github.com/matterport/Mask_RCNN)  
- [OpenCV](https://opencv.org/)  
- [Pandas](https://pandas.pydata.org/)  
- [Google Colab](https://colab.research.google.com/)  

---

## 📂 Estrutura do Projeto
```
├── mrcnn/                     # Implementação da Mask R-CNN
├── images1/                   # Imagens de treino e validação
├── images2/                   # Imagens para inferência
├── Seg_imagens_coletas/       # Anotações (JSON)
├── results.xlsx               # Resultados do treino
├── results_inference_bovine.xlsx   # Resultados da inferência
├── results_inference_bovine2.xlsx  # Resultados da inferência em outro dataset
├── Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow.ipynb
└── README.md
```

---

## 🚀 Como Executar

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow.git
cd Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

> ⚠️ Certifique-se de ter CUDA e cuDNN compatíveis com TensorFlow 2.5.

### 3. Treinar o modelo
No notebook:
```python
config = CustomConfig(class_number)
model = load_training_model(config)
train_head(model, dataset_train, dataset_val, config)
```

### 4. Salvar pesos treinados
```python
model.keras_model.save_weights("mask_rcnn_shapes_bovine.h5")
```

### 5. Inferência em novas imagens
```python
test_model, inference_config = load_inference_model(1, "mask_rcnn_shapes_bovine.h5")
```

---

## 📊 Resultados
- Segmentação precisa de bovinos em imagens.  
- Estimativa de peso com base em regressão linear da área segmentada.  
- Exportação automática dos resultados em planilhas Excel.  

---

## 📸 Exemplo de Saída
- Máscara segmentada sobreposta à imagem.  
- Informações de área, perímetro, comprimento, largura e peso predito exibidas na imagem.  

---

## 🤝 Contribuições
Sinta-se à vontade para abrir **issues** e enviar **pull requests**.  

---

## 📜 Licença
Este projeto é distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.  
