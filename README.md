# WebAppFlask
## Presentación
En este repositorio se describe cómo controlar un dron desde cualquier dispositivo conectado a internet, sin necesidad de instalar ninguna app en el dispositivo. Para ello se utiliza el framework Flask para implementer un servidor web en Python.   
El prepositorio proporciona códigos, vídeos y descripciones. También se proponen algunos retos que pueden ayudar a asentar los conceptos que se presentan.   
## Demo    
El vídeo muestra una demo de la aplicación que ejemplifica el tema. El simulador del dron (SITL) se controla desde una aplicación de escritorio desarrollada e Python y Tkinter y también desde un teléfono movil, mediante una web app desarrollada en Flask.    
[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DryezfzIUBrE)](https://www.youtube.com/watch?v=ryezfzIUBrE)     
## Arquitectura software
Este vídeo explica cómo está organizado el código. La comunicación entre el dispositivo móvil y el servidor web se realiza usando el protocolo HTTP, mediante operaciones GET y POST. La comunicación entre el servidor web y la aplicación de escritorio (desde la que se controla el dron) se realiza usando un broker que implementa el protocolo MQTT, en el que la comunicación se articula mediante publicaciones y subscripciones.    
[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DryezfzIUBrE)](https://www.youtube.com/watch?v=ryezfzIUBrE)    
Este vídeo es un pequeño paseo por el código de las aplicaciones.    
[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DryezfzIUBrE)](https://www.youtube.com/watch?v=ryezfzIUBrE)    
## Arquitectura alternativa
El vídeo muestra una arquitectura software alternativa en la que el dispositivo móvil solo se comunica con el servidor web para obtener la (única) página web. El script de esa página web permite al propio dispositivo móvil comunicarse comunicarse directamente con la aplicación de escritorio, a través del broker MQTT.    
[![](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DryezfzIUBrE)](https://www.youtube.com/watch?v=ryezfzIUBrE)    
## Instalación
Todo el código mostrado se puede descargar desde este repositorio. El código está organizado en tres carpetar: EstacionTierra, WebAppHTTP y WebAppMQTT.    
Para poner en marcha EstaciónTierra es necesario instalar las librerías *pymavlink* y *paho-mqtt*.    
Para poner en marcha WebAppHTTP es necesario instalar las librerías *Flask* y *paho-mqtt*. 
Para poner en marcha WebAppMQTT





