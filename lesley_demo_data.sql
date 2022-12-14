USE `lesley`;

LOCK TABLES `biography` WRITE;
INSERT INTO `biography` VALUES ('Lesley Paige Rutherford grew up in McLean, Virginia, a suburb of Washington DC. Her mother exposed her to art at a young age. Lesley took several art classes as a child, including courses at the Corcoran Gallery of Art. Once in college, at Denison University in Ohio, Lesley decided to major in Studio Art with an emphasis in photography. She graduated from Denison in 1997.\r\n\r\nIn 1998, Lesley moved to Los Angeles. Although she created a series of paintings during this time period, she decided to pursue a career in education. She earned her teaching credential and a Master of Arts in special education from California State University, Los Angeles. Lesley was hired as an elementary school teacher in Los Angeles.\r\n\r\nIn 2007, Lesley returned to art by creating a series of mixed media drawings. She drew these pieces with black ink and watercolor pencil. This art was displayed in Kaldi Coffee Shop in South Pasadena, California, where it was spotted by set designers for NBC\'s hit drama series, \"Parenthood.\" \"Parenthood\" purchased Lesley\'s entire portfolio and displayed many of the pieces on the show.\r\n\r\nLesley now works in colored pencil. For inspiration, she takes photographs throughout the city of Los Angeles. Lesley is particularly drawn to flea markets and farmers\' markets. She attempts to capture vibrant colors and dynamic displays. She also created a series of drawings that focus on the architecture of Chinatown.\r\n\r\nMost of Lesley\'s drawings contain black lines and a bold outline framing the picture. Some of the objects in her drawings are shaded, while other objects are areas of solid color. Her background in photography enables her to create well-balanced compositions. She is acutely aware of compositional elements such as negative shapes. This is evident throughout her portfolio.\r\n\r\nLesley\'s door series is a compilation of colored pencil drawings of doors throughout the world.  Specifically, Lesley drew doors from her travels to Rio de Janeiro, Panama, and Ireland.  She also has a collection of doors from Los Angeles.  Her latest doors contain graffiti and other urban markings. It is her believe that these markings reflect urban culture and have a rich historical context. \r\n\r\nIn the future, Lesley hopes to travel to urban areas throughout the world to collect more photographs for her drawings. She wishes to highlight the similarities in cultures, such as the abundance of farmers\' markets. Her art is ultimately apolitical and created in order to be harmonious and aesthetically pleasing.');
UNLOCK TABLES;

LOCK TABLES `fontfamilies` WRITE;
INSERT INTO `fontfamilies` VALUES (4,'fantasy'),(3,'monospaced'),(1,'sans-serif'),(5,'script'),(2,'serif');
UNLOCK TABLES;

LOCK TABLES `fonts` WRITE;
INSERT INTO `fonts` VALUES (1,'Lesley',1,2),(2,'Arial',1,NULL),(3,'Arial Black',1,2),(4,'Arial Narrow',1,2),(5,'Tahoma',1,2),(6,'Trebuchet MS',1,2),(7,'Verdana',1,2),(8,'Georgia',2,11),(9,'Lucida Bright',2,11),(10,'Palatino',2,11),(11,'Times New Roman',2,NULL),(12,'Courier New',3,2),(13,'Lucida Sans Typewriter',3,2),(14,'Papyrus',4,2);
UNLOCK TABLES;

LOCK TABLES `style` WRITE;
INSERT INTO `style` VALUES (1,254,100,88,96,0,1,2),(2,254,100,88,94,0,1,14),(3,281,68,89,91,25,1,1),(4,37,68,83,NULL,0,2,12),(5,254,100,88,96,0,1,2),(6,37,68,83,NULL,0,2,12),(7,254,100,88,96,0,1,2),(8,281,68,89,91,25,1,1),(9,37,68,83,NULL,0,2,12),(10,254,100,88,96,0,1,2);
UNLOCK TABLES;

LOCK TABLES `shuffle` WRITE;
INSERT INTO `shuffle` VALUES (0);
UNLOCK TABLES;
