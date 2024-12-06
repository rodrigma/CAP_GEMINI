# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from absl.testing import absltest
from absl.testing import parameterized
from dotenv import load_dotenv

import google.generativeai as genai
import pathlib
import os
import openpyxl
import json
import pandas as pd

load_dotenv()
api_key = os.environ.get('API_KEY')
genai.configure(api_key=os.environ["API_KEY"])
media = pathlib.Path(__file__).parents[1] / "third_party"
root = pathlib.Path(__file__).parents[1]

prompt_scotia="""
Con base en el documento adjunto, necesito que generes un conjunto de 20 casos de prueba en formato JSON, incluyendo escenarios positivos y negativos, para asegurar que se cubren todos los aspectos detallados en el documento de requerimientos de negocio para el desarrollo del sitio de ventas en línea. El conjunto debe incluir pruebas para todos los requisitos funcionales y no funcionales, así como casos de uso, según el documento, y asegurar que se valida cada funcionalidad descrita.

Los casos de prueba deben incluir pruebas de:

Antecedente  
Beneficiario
Descripción
Métodos de pago y promociones.
Beneficio Historia de Usuario
Módulos
Reglas de Negocio

Cada caso de prueba debe incluir los siguientes campos:

ID.
Tipo.
Propósito/Descripción.
Precondiciones.
Datos de entrada.
Acciones detalladas.
Resultados esperados.
Resultados actuales (para ser completados durante la ejecución).
Criterios de éxito/fallo.
Prioridad (alta, media o baja).
Autores.
Fecha de creación/modificación.

Por favor, genera casos de prueba de diferentes complejidades (alta, media y baja) y que tengan un mínimo de 5 pasos para asegurar una cobertura completa.

**Ejemplo de formato JSON:**
[
  {
    "ID": "TC_ALTA_001",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Verificar el correcto procesamiento de pagos con una tarjeta de crédito válida.",
    "Precondiciones": "Usuario registrado y autenticado, con productos en el carrito.",
    "Datos de entrada": {"tarjeta": "4111 1111 1111 1111", "fecha_expiracion": "12/25", "cvv": "123"},
    "Acciones": ["Paso 1.- Ingresar al carrito", "Paso 2.- Proceder al checkout", "Paso 3.- Ingresar los datos de la tarjeta", "Confirmar el pago"],
    "Resultados esperados": "El pago se procesa correctamente y el pedido se confirma.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El pago es aprobado y el pedido aparece en la cuenta del usuario.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_002",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Validar la autenticación de dos factores en el proceso de inicio de sesión.",
    "Precondiciones": "Usuario registrado con autenticación de dos factores activada.",
    "Datos de entrada": {"usuario": "usuario1", "contraseña": "ContraseñaSegura123", "token": "987654"},
    "Acciones": ["Paso 1.- Navegar a la página de inicio de sesión", "Paso 2.- Ingresar usuario y contraseña", "Paso 3.- Ingresar token de autenticación", "Hacer clic en 'Iniciar sesión'"],
    "Resultados esperados": "El usuario puede acceder a su cuenta después de la verificación de dos factores.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El usuario es autenticado exitosamente.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_003",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Validar la capacidad del sistema para manejar un alto volumen de usuarios concurrentes en un evento promocional.",
    "Precondiciones": "Servidor en modo de prueba de estrés.",
    "Datos de entrada": {"usuarios_concurrentes": "5000"},
    "Acciones": ["Paso 1.- Realizar 5000 conexiones simultáneas al sitio", "Paso 2.- Realizar compras en masa desde diferentes cuentas"],
    "Resultados esperados": "El sitio mantiene el rendimiento sin caídas.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El sistema no experimenta caídas ni errores de rendimiento.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_004",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Verificar que el sistema permita devoluciones dentro de los primeros 30 días después de la compra.",
    "Precondiciones": "Usuario registrado con un pedido realizado hace menos de 30 días.",
    "Datos de entrada": {"pedido_id": "12345", "razon_devolucion": "Producto defectuoso"},
    "Acciones": ["Paso 1.- Navegar a 'Mis pedidos'", "Paso 2.- Seleccionar el pedido", "Paso 3.- Solicitar devolución"],
    "Resultados esperados": "El sistema genera una etiqueta de devolución.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "Se genera la devolución correctamente y se notifica al usuario.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_005",
    "Tipo": "Negativo",
    "Propósito/Descripción": "Asegurar que las notificaciones de stock agotado se envíen correctamente.",
    "Precondiciones": "Producto en el carrito agotado.",
    "Datos de entrada": {"producto_id": "56789"},
    "Acciones": ["Paso 1.- Agregar producto al carrito", "Paso 2.- Intentar finalizar compra", "Paso 3.- Observar notificación de stock"],
    "Resultados esperados": "Se notifica que el producto está agotado.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El sistema muestra un mensaje de producto agotado y no permite completar la compra.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  }
]"""


prompt="""
Con base en el documento adjunto, necesito que generes un conjunto de 20 casos de prueba en formato JSON, incluyendo escenarios positivos y negativos, para asegurar que se cubren todos los aspectos detallados en el documento de requerimientos de negocio para el desarrollo del sitio de ventas en línea. El conjunto debe incluir pruebas para todos los requisitos funcionales y no funcionales, así como casos de uso, según el documento, y asegurar que se valida cada funcionalidad descrita.

Los casos de prueba deben incluir pruebas de:

Registro y autenticación de usuarios.   
Navegación y búsqueda en el catálogo de productos.
Carrito de compras y proceso de checkout.
Métodos de pago y promociones.
Gestión de inventario.
Envío y entrega de productos.
Soporte postventa, devoluciones y reembolsos.
Notificaciones y sistema de alertas.
Programa de fidelidad y recompensas.
Analítica y reportes.
Rendimiento, seguridad, compatibilidad, escalabilidad y disponibilidad del sitio.

Cada caso de prueba debe incluir los siguientes campos:

ID.
Tipo.
Propósito/Descripción.
Precondiciones.
Datos de entrada.
Acciones detalladas.
Resultados esperados.
Resultados actuales (para ser completados durante la ejecución).
Criterios de éxito/fallo.
Prioridad (alta, media o baja).
Autores.
Fecha de creación/modificación.

Por favor, genera casos de prueba de diferentes complejidades (alta, media y baja) y que tengan un mínimo de 5 pasos para asegurar una cobertura completa.

**Ejemplo de formato JSON:**
[
  {
    "ID": "TC_ALTA_001",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Verificar el correcto procesamiento de pagos con una tarjeta de crédito válida.",
    "Precondiciones": "Usuario registrado y autenticado, con productos en el carrito.",
    "Datos de entrada": {"tarjeta": "4111 1111 1111 1111", "fecha_expiracion": "12/25", "cvv": "123"},
    "Acciones": ["Paso 1.- Ingresar al carrito", "Paso 2.- Proceder al checkout", "Paso 3.- Ingresar los datos de la tarjeta", "Confirmar el pago"],
    "Resultados esperados": "El pago se procesa correctamente y el pedido se confirma.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El pago es aprobado y el pedido aparece en la cuenta del usuario.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_002",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Validar la autenticación de dos factores en el proceso de inicio de sesión.",
    "Precondiciones": "Usuario registrado con autenticación de dos factores activada.",
    "Datos de entrada": {"usuario": "usuario1", "contraseña": "ContraseñaSegura123", "token": "987654"},
    "Acciones": ["Paso 1.- Navegar a la página de inicio de sesión", "Paso 2.- Ingresar usuario y contraseña", "Paso 3.- Ingresar token de autenticación", "Hacer clic en 'Iniciar sesión'"],
    "Resultados esperados": "El usuario puede acceder a su cuenta después de la verificación de dos factores.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El usuario es autenticado exitosamente.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_003",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Validar la capacidad del sistema para manejar un alto volumen de usuarios concurrentes en un evento promocional.",
    "Precondiciones": "Servidor en modo de prueba de estrés.",
    "Datos de entrada": {"usuarios_concurrentes": "5000"},
    "Acciones": ["Paso 1.- Realizar 5000 conexiones simultáneas al sitio", "Paso 2.- Realizar compras en masa desde diferentes cuentas"],
    "Resultados esperados": "El sitio mantiene el rendimiento sin caídas.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El sistema no experimenta caídas ni errores de rendimiento.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_004",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Verificar que el sistema permita devoluciones dentro de los primeros 30 días después de la compra.",
    "Precondiciones": "Usuario registrado con un pedido realizado hace menos de 30 días.",
    "Datos de entrada": {"pedido_id": "12345", "razon_devolucion": "Producto defectuoso"},
    "Acciones": ["Paso 1.- Navegar a 'Mis pedidos'", "Paso 2.- Seleccionar el pedido", "Paso 3.- Solicitar devolución"],
    "Resultados esperados": "El sistema genera una etiqueta de devolución.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "Se genera la devolución correctamente y se notifica al usuario.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_005",
    "Tipo": "Negativo",
    "Propósito/Descripción": "Asegurar que las notificaciones de stock agotado se envíen correctamente.",
    "Precondiciones": "Producto en el carrito agotado.",
    "Datos de entrada": {"producto_id": "56789"},
    "Acciones": ["Paso 1.- Agregar producto al carrito", "Paso 2.- Intentar finalizar compra", "Paso 3.- Observar notificación de stock"],
    "Resultados esperados": "Se notifica que el producto está agotado.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El sistema muestra un mensaje de producto agotado y no permite completar la compra.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  }
]"""

prompt_bnt = """
Con base en el documento adjunto, necesito que generes un conjunto de 15 casos de prueba en formato JSON, incluyendo escenarios positivos y negativos, para asegurar que se cubren todos los aspectos detallados en el documento de requerimientos de negocio. El conjunto debe incluir pruebas para todos los requisitos funcionales y no funcionales, así como casos de uso, según el documento, y asegurar que se valida cada funcionalidad descrita.

Cada caso de prueba debe incluir los siguientes campos:
ID.
Tipo.
Propósito/Descripción.
Precondiciones.
Datos de entrada.
Acciones detalladas.
Resultados esperados.
Resultados actuales (para ser completados durante la ejecución).
Criterios de éxito/fallo.
Prioridad (alta, media o baja).
Autores.
Fecha de creación/modificación.

Por favor, genera casos de prueba de diferentes complejidades (alta, media y baja) y que tengan un mínimo de 5 pasos para asegurar una cobertura completa.
**Ejemplo de formato JSON:**
[
  {
    "ID": "TC_ALTA_001",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Verificar el correcto procesamiento de pagos con una tarjeta de crédito válida.",
    "Precondiciones": "Usuario registrado y autenticado, con productos en el carrito.",
    "Datos de entrada": {"tarjeta": "4111 1111 1111 1111", "fecha_expiracion": "12/25", "cvv": "123"},
    "Acciones": ["Paso 1.- Ingresar al carrito", "Paso 2.- Proceder al checkout", "Paso 3.- Ingresar los datos de la tarjeta", "Confirmar el pago"],
    "Resultados esperados": "El pago se procesa correctamente y el pedido se confirma.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El pago es aprobado y el pedido aparece en la cuenta del usuario.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_002",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Validar la autenticación de dos factores en el proceso de inicio de sesión.",
    "Precondiciones": "Usuario registrado con autenticación de dos factores activada.",
    "Datos de entrada": {"usuario": "usuario1", "contraseña": "ContraseñaSegura123", "token": "987654"},
    "Acciones": ["Paso 1.- Navegar a la página de inicio de sesión", "Paso 2.- Ingresar usuario y contraseña", "Paso 3.- Ingresar token de autenticación", "Hacer clic en 'Iniciar sesión'"],
    "Resultados esperados": "El usuario puede acceder a su cuenta después de la verificación de dos factores.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El usuario es autenticado exitosamente.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_003",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Validar la capacidad del sistema para manejar un alto volumen de usuarios concurrentes en un evento promocional.",
    "Precondiciones": "Servidor en modo de prueba de estrés.",
    "Datos de entrada": {"usuarios_concurrentes": "5000"},
    "Acciones": ["Paso 1.- Realizar 5000 conexiones simultáneas al sitio", "Paso 2.- Realizar compras en masa desde diferentes cuentas"],
    "Resultados esperados": "El sitio mantiene el rendimiento sin caídas.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El sistema no experimenta caídas ni errores de rendimiento.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_004",
    "Tipo": "Positivo",
    "Propósito/Descripción": "Verificar que el sistema permita devoluciones dentro de los primeros 30 días después de la compra.",
    "Precondiciones": "Usuario registrado con un pedido realizado hace menos de 30 días.",
    "Datos de entrada": {"pedido_id": "12345", "razon_devolucion": "Producto defectuoso"},
    "Acciones": ["Paso 1.- Navegar a 'Mis pedidos'", "Paso 2.- Seleccionar el pedido", "Paso 3.- Solicitar devolución"],
    "Resultados esperados": "El sistema genera una etiqueta de devolución.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "Se genera la devolución correctamente y se notifica al usuario.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  },
  {
    "ID": "TC_ALTA_005",
    "Tipo": "Negativo",
    "Propósito/Descripción": "Asegurar que las notificaciones de stock agotado se envíen correctamente.",
    "Precondiciones": "Producto en el carrito agotado.",
    "Datos de entrada": {"producto_id": "56789"},
    "Acciones": ["Paso 1.- Agregar producto al carrito", "Paso 2.- Intentar finalizar compra", "Paso 3.- Observar notificación de stock"],
    "Resultados esperados": "Se notifica que el producto está agotado.",
    "Resultados actuales": "",
    "Criterios de éxito/fallo": "El sistema muestra un mensaje de producto agotado y no permite completar la compra.",
    "Prioridad": "Alta",
    "Autores": "Rodrigo Martínez",
    "Fecha de creación/modificación": "2024-10-10"
  }
]
"""

#file_name_xlsx = "manual_tcs_demo.xlsx"
#file_json = "manual_tcs.json"

file_name_xlsx = "manual_tcs_demo_scotia.xlsx"
file_json = "manual_tcs_bnt.json"

# Ajustar el ancho de todas las columnas al contenido más largo
def set_column_width(worksheet):
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value)) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = max_length + 2

def guardar_json(data, archivo):
    """Guarda un objeto en un archivo.

    Args:
        data (dict): El objeto Python a serializar.
        archivo (str): La ruta del archivo.
    """

    if os.path.exists(archivo):
        print(f"El archivo {archivo} ya existe. Se sobrescribirá.")
    else:
        print(f"Creando el archivo {archivo}")

    with open(archivo, 'w',encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class UnitTests(parameterized.TestCase): 
    @absltest.skip("This test is skipped for now")
    def test_text_gen_text_only_prompt(self):
        with open(root / file_json, 'r',encoding='utf-8') as archivo_json:
            # Leer y convertir el archivo a un diccionario
            contenido_json = json.load(archivo_json,)
        i = 0
        for tc in contenido_json:
            tc_id = tc['ID']
            
            # Convertir el diccionario a un string con formato JSON
            atc_str = json.dumps(tc, indent=4, ensure_ascii=False)
            
            # [START text_gen_text_only_prompt]
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(os.environ.get('PROMPT_ATC') + atc_str )
            full_text = response.text
            full_text = full_text[7:]+"$_$"
            full_text = full_text.replace("```","/*").replace("$_$","*/")
            # [END text_gen_text_only_prompt]
            # Guardar el contenido en un archivo .java
            with open(tc_id+".java", 'w',encoding='utf-8') as archivo_java:
                archivo_java.write(full_text)
            i+=1
  
    def test_text_gen_multimodal_pdf(self):
   
        #pdf_file = "Requerimiento Negocio demo.pdf"
        pdf_file = "HU01_OFI.pdf"
        
        # [START text_gen_multimodal_pdf]
        model = genai.GenerativeModel("gemini-1.5-flash")
        sample_pdf = genai.upload_file(media / pdf_file)
        response = model.generate_content([prompt_scotia, sample_pdf])
        #print(f"{response.text=}")
        # [END text_gen_multimodal_pdf]
        full_text = response.text
        full_text = full_text.replace("\n","")[7:]
        full_text = full_text[0:len(full_text)-3]
        json_obj = json.loads(full_text)

        #Guardar objeto JSON en archivo JSON
        guardar_json(json_obj, file_json)

        #for i in range(num_tcs):
        # Convertir el diccionario a un DataFrame
        df = pd.json_normalize(json_obj)
        # Exportar el DataFrame a un archivo Excel
        df.to_excel(file_name_xlsx, index=False)
        
        # Leer el archivo Excel
        df = pd.read_excel(file_name_xlsx)
        # Exportar a un nuevo archivo Excel con el ajuste de ancho
        with pd.ExcelWriter(file_name_xlsx) as writer:
            df.to_excel(writer, sheet_name='Hoja1', index=False)
            worksheet = writer.sheets['Hoja1']
            set_column_width(worksheet)
    
    @absltest.skip("This test is skipped for now")
    def test_text_gen_multimodal_pdf_bnt(self):
        
        
        # [START text_gen_multimodal_pdf]
        model = genai.GenerativeModel("gemini-1.5-flash")
        sample_pdf = genai.upload_file(media / "Banorte_Levantamiento_de_Requerimiento.pdf")
        response = model.generate_content([prompt_bnt, sample_pdf])
        #print(f"{response.text=}")
        # [END text_gen_multimodal_pdf]
        full_text = response.text
        full_text = full_text.replace("\n","")[7:]
        full_text = full_text[0:len(full_text)-3]
        json_obj = json.loads(full_text)

        #Guardar objeto JSON en archivo JSON
        guardar_json(json_obj, file_json)

        #for i in range(num_tcs):
        # Convertir el diccionario a un DataFrame
        df = pd.json_normalize(json_obj)
        # Exportar el DataFrame a un archivo Excel
        df.to_excel(file_name_xlsx, index=False)
        
        # Leer el archivo Excel
        df = pd.read_excel(file_name_xlsx)
        # Exportar a un nuevo archivo Excel con el ajuste de ancho
        with pd.ExcelWriter(file_name_xlsx) as writer:
            df.to_excel(writer, sheet_name='Hoja1', index=False)
            worksheet = writer.sheets['Hoja1']
            set_column_width(worksheet)


if __name__ == "__main__":
    absltest.main()
