# Cleaning Data

## Tabla de Contenidos

- [Descripción de los problemas]
- [Propuesta de formato JSON]
- [Metodología de limpieza]
- [Mejoras propuestas]

## Descripción de los problemas
### Elementos duplicados
Una parte importante del análisis de datos es analizar valores duplicados y tratarlos según las circunstancias. Mediante el método duplicated() de Pandas hemos obtenido los valores duplicados de la columna CrimeId. Estos valores no coincidían en todos sus otros campos y por eso se decidió no eliminarlos. Solo comprobamos la columna CrimeId porque podría actuar como clave primaria de esta tabla, para el resto de las columnas no era necesario hacer esta comprobación ya que admiten valores duplicados sin que eso genere ningún tipo de problema.

La solución por la que se ha optado ha sido modificar los valores de CrimeId duplicados para no perder información, modificando el valor por el último valor de la columna CrimeId + 1.
```
def replaceDuplicateIds(df, columnId):
    duplicated_ids = findDuplicateIds(df, columnId)
    new_val = df[columnId].iloc[-1] + 1
    for i in duplicated_ids.index:
        df.loc[i, [columnId]] = new_val
        new_val=new_val+1
```
### Tratamiento de texto
Dentro de nuestro dataset debemos asegurarnos que los campos de texto sean coherentes. Si encontramos caracteres extraños, espacios en blanco, etc. cuando tratemos de procesarlo van a surgir problemas. Para controlar esto, hemos revisado los siguientes aspectos:

• Normalización del texto: para evitar problemas de formato de texto se ha llevado a cabo una normalización muy sencilla, en la cual las columnas que se refieran a nombres propios comenzarán todas sus palabras con la primera letra mayúsculas haciendo uso del método title(), mientras que aquellas columnas que no se refieran a un nombre propio, tendrán todas sus palabras en mayúsculas, utilizando el método upper(). Del mismo modo, podría haberse elegido que todas fuesen minúsculas, pero en este caso optamos por la otra opción.

Con esto evitamos que haya confusiones como la que se produce en la columna City, por ejemplo, en la cual toma como dos valores distintos a ‘San Francisco’ y a ‘SAN FRANCISCO’. Para acceder a los valores de una columna lo haremos mediante el método value_counts().

• Eliminar espacios en blanco: aprovechando el ejemplo anterior, podemos observar que uno de los elementos de la columna City es una S, pero tiene espacios blancos a su alrededor. Estos espacios en blanco nos pueden dar problemas en un futuro y no son más que caracteres sin contenido (espacio, tabulación, etc.), por lo tanto, hemos decidido eliminarlos haciendo uso del método strip() que elimina los espacios blancos a la derecha y a la izquierda del string.

• Eliminar caracteres extraños: los caracteres extraños pueden confundir a los modelos de inteligencia artificial, creando ruido e impidiendo una correcta comprensión de la palabra a la que se adjunta. Es por esto que, hemos decidido eliminar una serie de caracteres extraños como podrían ser *, $, % entre otros, haciendo uso del método replace.

Estos 3 pasos serán realizados al comienzo de nuestro script de transformación y se aplicarán a todas aquellas columnas que sean de tipo Object. Para ello hemos utilizado distintos arrays que recorreremos llamando a los distintos métodos de tratamiento.
```
str_columns = ['OriginalCrimeTypeName', 'Disposition', 'Address', 'City', 'State', 'AddressType']
all_mayus_columns = ['OriginalCrimeTypeName', 'Disposition','AddressType']
first_mayus_columns = ['Address', 'City']

for str_column in str_columns:
  cleanStrangeCharacters(data_act_01, str_column)
  cleanWhiteSpaces(data_act_01, str_column)
for all_mayus_column in all_mayus_columns:
  setAllMayus(data_act_01, all_ mayus_column)
for first_mayus_column in first_mayus_columns:
  setFirstMayus(data_act_01, first_mayus_column)
```
### Tratamiento de fechas y horas
Al igual que sucede con el texto, es importante realizar un tratamiento a las fechas y horas de nuestro dataset para que puedan ser reconocidas como fechas por nuestros sistemas. Lo primero que vimos fue que las fechas no venían en un formato reconocido como fecha, así que las transformamos haciendo uso del método to_datetime(). Una vez tenían el formato correcto, comprobamos los rangos de las fechas. En caso de encontrar una fecha mayor al día actual, esta sería modificada y se pondría la actual, como se muestra en el siguiente código:
```
def setMaxDateNow(df, columnId):
  if(columnId == 'OffenseDate'):
    now = datetime.today().strftime("%d --%m --%Y 00:00:
  else:
    now = datetime.today().strftime("%d --%m --%Y %H:%M:%
  wrong_date = df.loc[(df[columnId] > now)]
  df.loc[wrong_date.index, columnId] = now
```
Además de esto, realizamos una comparación entre la columna CallTime y las horas y minutos de la columna CallDateTime, obteniendo como resultado que en una de las filas los valores diferían. Decidimos no hacer tratamiento de esto, ya que la columna CallTime nos parecía redundante y la íbamos a eliminar, como veremos más adelante.
### Datos incoherentes
Pueden existir algunos datos que nos resulten incoherentes o raros respecto al resto de datos de las columnas. Estos tienen que ser corregidos de manera cuidadosa para tratar de evitar perder datos. En nuestro caso tras revisar los tipos de datos de las columnas detectamos algunos errores que corregimos de las siguiente manera:

• En la columna City como hemos visto antes, había un valor ‘S’, que por descarte se ha sustituido por ‘San Francisco’. Lo mismo sucede con la columna AgencyId en la cual encontramos el valor ‘Intersectioon’ que claramente se trataba de un error y se refería a ‘Intersection’. Este tipo de errores, al ser puntuales se han corregido prácticamente a mano alzada. En esta última columna también se decidió actuar sobre el valor ‘1’, el cual se podía ver que se trataba de ‘Intersection’ ya que, para su fila, en la columna de direcciones había dos elementos en todos los casos.

• Existen otras columnas, como AgencyId en las cuales se ha tomado la decisión de cambiar los valores por la moda de los que había. De esta forma queda más automatizado el proceso, pero se corre más riesgo de cometer algún error.

### Valores faltantes
Para poder detectar los valores faltantes de una columna o un dataset se hará mediante el método isna().sum() que nos devolverá el total de datos que faltan en el dataset o la columna. En nuestro caso hemos evitado a toda costa eliminar filas en las que hubiese datos faltantes, a cambio, los hemos sustituido por otros siguiendo algunos criterios.

Para la columna City, dado que era la que más valores faltantes tenía, se ha decidido rellenarlos con ‘Not Recorded’ haciendo uso de la función fillna() y siguiendo la nomenclatura establecida en el dataset en la columna Disposition. Por otra parte, para la columna State que también tenía valores faltantes, se ha decidido rellenarlos con la moda de esta columna, que se calcula fácilmente llamando al método mode().

### Datos irrelevantes
Los datos irrelevantes favorecen la ralentización y la confusión en cualquier análisis. Por ello hemos tratado de ver que era relevante y necesario y eliminar el resto. Para el caso de la columna Range está claro que es innecesaria. Por ello se ha procedido a eliminarla, no sin antes comprobar si está vacía. Algo similar sucede para la columna CallTime, la cual resultaba ser redundante y decidimos prescindir de ella.

## Propuesta de formato JSON
```
{
  "CrimeId":160903280,
  "OriginalCrimeTypeName":"ASSAULT \/ BATTERY",
  "OffenseDate":"2016-03-30",
  "CallDateTime":"2016-03-30 18:42:00",
  "Disposition":"REP",
  "Address":"100 Block Of Chilton Av",
  "City":"San Francisco",
  "State":"CA",
  "AgencyId":1,
  "AddressType":"PREMISE ADDRESS"
}
```
Se propone como resultado un archivo JSON con la estructura columna:valor. En él se pueden encontrar todos los aspectos tratados en el apartado anterior ya corregidos y que trataremos a continuación de forma breve:

• CrimeId: número entero que actuará como identificador, se han modificado los elementos duplicados para no hacerlos desaparecer.

• OriginalCrimeTypeName: se le ha realizado una limpieza de caracteres extraños y espacios en blanco, además, se han puesto en mayúsculas todos sus valores como se explicó anteriormente.

• OffenseDate: se hace un tratamiento para evitar que los valores rebasen la fecha límite establecida.

• CallDateTime: al igual que el anterior, se evita que los valores sean superiores al momento actual.

• Disposition: aparentemente no necesitaba ningún tratamiento, todos los códigos eran correctos al buscarlos en internet. Simplemente nos hemos asegurado de hacerle un tratamiento de texto.

• Address: al igual que el anterior, el tratamiento ha sido genérico al texto.

• City: se han completado los valores nulos y se han corregido otros erróneos.

• State: se han rellenado los valores nulos con la moda de esta columna.

• AgencyId: se han modificado los valores erróneos por la moda de la columna.

• AddressType: se ha realizado la corrección de errores ortográficos y valores erróneos.

• Se ha decido eliminar la columna Range ya que estaba vacía y la columna CallTime, porque nos resultaba redundante porque teniendo la columna CallDateTime tenemos ahí la hora incorporada.

##Metodología de limpieza
• Entender el dataset: es necesario parar y leer cada una de las columnas y los valores que tienen para ver si el dataset es comprensible. En caso de no ser así buscaremos información que nos ayude.

• Eliminar valores duplicados o irrelevantes: eliminar los valores no deseados, como aquellos que están duplicados (se debe tener cuidado, ya que, en ocasiones, aunque parezca que dos filas están duplicadas es posible que alguno de sus caracteres sea distinto) y los valores irrelevantes, que son aquellos que no encajan con el problema que estas analizando o que no aportan ninguna información.

• Corregir errores estructurales: estos errores engloban a nomenclaturas extrañas, errores tipográficos, mayúsculas incorrectas, espacios en blanco, etc. pero también se debe convertir los valores al tipo de dato que les corresponda.

• Corregir valores atípicos: los valores atípicos son aquellos que no parecen encajar con los datos que se están analizando. Si estas seguro de esto, puedes modificar su valor por el que consideres correcto, o en caso de ser irrelevante para el análisis, podrás eliminarlo.

• Tratar los datos faltantes: estos datos no pueden ser ignorados, por ello se puede tomar alguna de las siguientes alternativas.

a. Modificar los valores para que no sean nulos, usando términos como ‘No aplica’, ‘No data’ o similares.

b. Rellenar los valores nulos basándonos en otras observaciones.

c. Como última opción, eliminarlos. Debemos ser conscientes de que mediante este proceso perdemos información.

## Mejoras propuestas
### Homogeneizar las direcciones
La primera de las mejoras que propongo sería tratar de hacer las direcciones más homogéneas. En vez de tener un texto libre de entrada, en primer lugar, habría un selector del tipo de dirección. Por ejemplo, en función de si es una dirección común o una intersección se mostrarían unos campos en concreto. Con esto conseguimos que, si marcamos el tipo de dato intersección en el selector, entonces tengamos unos campos para meter dos direcciones; si por el contrario marcamos localización común solo tendremos unos campos para meter una única dirección.

Además de esto, a la hora de introducir la dirección tendremos unas casillas especificas para meter calle, avenida, numero de bloque, etc. Una vez tengamos estos datos les damos el formato que más nos interese y los almacenamos en el campo dirección. De este modo todas las direcciones tendrían un aspecto similar.
### Crear subcategorías de crímenes
Dado que existe un gran numero de tipos de crímenes, la propuesta que hago para mejorar consiste en dividir los crímenes por categorías. A la hora de introducir un crimen nuevo, habrá una serie de selectores que poco a poco se vayan haciendo más concretos.

Por ejemplo, supongamos que tenemos distintos tipos de crímenes: delitos contra las personas, delitos contra el patrimonio, delitos de seguridad vial. Cuando se va a introducir un nuevo crimen se selecciona una de estas categorías, que a su vez desbloquea otra subcategoría, como podría ser, en el caso de delitos contra el patrimonio, robo, hurto y que a su vez estos tuviesen otra categoría más específica como robo con fuerza o robo con violencia. De este modo estaría más categorizado el tipo de delito.

Otra opción es asignar a cada tipo de delito un código numérico o alfanumérico y referirse a ellos directamente por ese código de delito. Esto facilitaría mucho su clasificación y búsqueda.
