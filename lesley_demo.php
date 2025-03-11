<?php
	require_once '../paths.php';
	require_once 'artpiece.php';
    require_once 'database.php';

    # Add famous images and information from Wikipedia for demo purposes
    add_image("Windmill at Wijk bij Duurstede", 32, 39, 1901, 0, NULL,
        "The Windmill of Wijk bij Duurstede (c. 1670) is an oil on canvas painting by the Dutch painter Jacob van Ruisdael. It is an example of Dutch Golden Age painting and is now in the collection of the Amsterdam Museum, on loan to the Rijksmuseum. The painting shows Wijk bij Duurstede, a riverside town about 20 kilometers from Utrecht, with a dominating cylindrical windmill, harmonised by the lines of river bank and sails, and the contrasts between light and shadow working together with the intensified concentration of mass and space. [1] The attention to detail is remarkable. Art historian Seymour Slive reports that both from an aeronautical engineering and a hydrological viewpoint the finest levels of details are correct, in the windmill's sails and the river's waves respectively.[2]",
        "https://en.wikipedia.org/wiki/Windmill_at_Wijk_bij_Duurstede",
        "https://upload.wikimedia.org/wikipedia/commons/d/df/The_Mill.jpg");
    add_image("A Sunday Afternoon on the Island...", 99, 81.75, 1901, 1, 30,
        "A Sunday Afternoon on the Island of La Grande Jatte was painted from 1884 to 1886 and is Georges Seurat's most famous work. A leading example of pointillist technique, executed on a large canvas, it is a founding work of the neo-impressionist movement. Seurat's composition includes a number of Parisians at a park on the banks of the River Seine. It is in the collection of the Art Institute of Chicago.",
        "https://en.wikipedia.org/wiki/A_Sunday_Afternoon_on_the_Island_of_La_Grande_Jatte",
        "https://upload.wikimedia.org/wikipedia/commons/7/7d/A_Sunday_on_La_Grande_Jatte%2C_Georges_Seurat%2C_1884.jpg");
    add_image("Finding of the Body of Saint Mark", 99, 99, 1901, 1, 1500, 
        "The painting was commissioned by Tommaso Rangone, the “grand guardian” of the Scuola Grande di San Marco in Venice, from Tintoretto as part of a series of large canvases depicting Venice's acquisition of the body of Saint Mark. The painting shows Venetians busily removing corpses from tombs along the right wall and from a crypt in the background. In the left foreground, Saint Mark surrounded by a faint halo appears and beseeches the Venetians to stop as his body has been found and lies pale at his feet, strewn on an oriental rug. In the center of the canvas, an elder (portrait of Rangone) kneels, acknowledging the miracle. Elsewhere in the room, the figures are either astonished or oblivious to the apparition.",
        "https://en.wikipedia.org/wiki/Finding_of_the_Body_of_Saint_Mark",
        "https://upload.wikimedia.org/wikipedia/commons/8/89/Jacopo_Tintoretto_-_Finding_of_the_body_of_St_Mark_-_Yorck_Project.jpg");
    add_image("The Peaceable Kingdom", 17.5, 23.5, 1901, 0, NULL, 
        "By Edward Hicks",
        "https://en.wikipedia.org/wiki/Edward_Hicks",
        "https://upload.wikimedia.org/wikipedia/commons/6/62/Edward_Hicks_-_Peaceable_Kingdom.jpg");

        # Publish each image (except one, to show an unpublished piece)
        $db = database::connect();
        $db->beginTransaction();
        for ($i=1; $i<=3; $i++) {
            updateDB($db, $i);
        }
        $db->commit();

// Publish a piece by copying the id to the sequence number
function updateDB($db, $id) {
    $sql = "UPDATE `info` SET `sequence` = :sequence WHERE `id` = :id;";
    $stmtnull = $db->prepare($sql);
    $stmtnull->bindValue(":sequence", $id, PDO::PARAM_INT);
    $stmtnull->bindValue(":id", $id, PDO::PARAM_INT);
    if (!$stmtnull->execute()) {
        die('Error executing query: ' . $db->errorInfo());
    }
}

// Use artpiece class to add an image file and information to the database & website
function add_image($title, $width, $height, $year, $sale, $price, $desc, $wiki_url, $image_url) {
    $file_name = artpiece::createfilename($title);
    $file_path = UPLOAD_ORIGINALS['sys'] . $file_name . '.jpg';
    download_image1($image_url, $file_path);
    $artpiece = new artpiece();
    $artpiece->addfile($file_name);
    $artpiece->getfile()->setcropall(0,0,0,0);
    $artpiece->getfile()->setrotation(0);
    $artpiece->getfile()->createwatermarked();
    $artpiece->getfile()->createthumbnail();
    $artpiece->getfile()->writewatermarked();
    $artpiece->getfile()->writethumbnail();
    $artpiece->getfile()->destroywatermarked();
    $artpiece->getfile()->destroythumbnail();
    $artpiece->addinfo($title, $width, $height, $year, $sale, $price, $desc, $wiki_url, NULL);
    $artpiece->movefiles();
    $artpiece->setdb();
    unset($artpiece);  
}

// Function taken from https://stackoverflow.com/a/22734061/3130769
// takes URL of image and Path for the image as parameter
function download_image1($image_url, $image_file) {
    $fp = fopen ($image_file, 'w+');              // open file handle

    $ch = curl_init($image_url);
    // curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // enable if you want
    curl_setopt($ch, CURLOPT_FILE, $fp);          // output to file
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10000);      // some large value to allow curl to run for a long time
    curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0');
    // curl_setopt($ch, CURLOPT_VERBOSE, true);   // Enable this line to see debug prints
    curl_exec($ch);

    curl_close($ch);                              // closing curl handle
    fclose($fp);                                  // closing file handle
}

?>
