<!DOCTYPE html>
<html>
<head>
    <title>Grid</title>
    <style>
        * {
            font-family: Verdana, monospace;
            font-size: 6px;
            color: #303030;
        }

        body {
            background-color: #000000;
        }

        .warehouse {
            background-color: #ff0000;
            color: #ffffff;
        }
    </style>
</head>
<body>
<?php
$warehouses = [
    [113, 179],
    [234, 599],
    [195, 89],
    [215, 207],
    [220, 326],
    [182, 193],
    [75, 418],
    [228, 140],
    [310, 26],
    [297, 423],
];

$rendered_warehouses = [];
foreach ($warehouses as $id => $location) {
    $rendered_warehouses[$location[0]][$location[1]] = $id;
}

for ($i = 0; $i < 400; $i++) {
    for ($j = 0; $j < 600; $j++) {
        $code = '&#9632;';
        if (isset($rendered_warehouses[$i][$j])) {
            $code = '<span class="warehouse">&#8962;</span>';
        }
        echo '<span title="' . $i . ',' . $j . '">' . $code . '</span>';
    }
    echo '<br>' . PHP_EOL;
}
?>
</table>
</body>
</html>