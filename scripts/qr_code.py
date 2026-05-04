## Geração de QRCode mais elaborado:
#import qrcode
## Importar a biblioteca que trata as imagens no QR Code conforme linha abaixo
#from qrcode.image.styledpil import StyledPilImage
#
#qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H) # Corrigindo alguns erros na inserção da imagem
#
## Apontando o link de acesso do QR Code
#qr.add_data("https://www.ifood.com.br/delivery/rio-de-janeiro-rj/scada-cafe---cinesystem-botafogo/7de61e90-2227-4a2a-812f-7498449de72f?utm_medium=share")
#
#imagem = qr.make_image( # Instruções para inserção da imagem
#    image_factory=StyledPilImage, # Apontando o Pillow para utilização da imagem
#    embeded_image_path="Logo Scada.png" # Apontando a imagem a ser colocada no QR Code
#)
#imagem.save("qrcode2.png") # Salvar imagem


import qrcode
from qrcode.constants import ERROR_CORRECT_L

url = "https://bit.ly/4uNv6Nl"  # 🔥 link encurtado através do bit.ly

qr = qrcode.QRCode(
    version=2,  # controla complexidade
    error_correction=ERROR_CORRECT_L,  # mínimo → QR mais simples
    box_size=10,
    border=2
)

qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")

img.save("qrcode_ifood_simples.png")