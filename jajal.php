<?php
$inputJSON = file_get_contents('php://input');
print_r($inputJSON);
echo PHP_EOL;

$headers = array();
foreach ($_SERVER as $key => $value) {
    if (strpos($key, 'HTTP_') === 0) {
        $headers[str_replace(' ', '', ucwords(str_replace('_', ' ', strtolower(substr($key, 5)))))] = $value;
    }
}

print_r($headers);