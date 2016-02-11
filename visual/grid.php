<!DOCTYPE html>
<html>
<head>
    <title>Grid</title>
    <style>
        * {
            font-family: Verdana, monospace;
            font-size: 10px;
        }

        td {
            border: 1px dashed gray;
            min-width: 16px;
            min-height: 16px;
            text-align: center;
        }

        .warehouse {
            background-color: #ff0000;
            color: #ffffff;
        }
    </style>
</head>
<body>
<table>
    <?php
    $warehouses = [
        [5, 5],
        [9, 15],
    ];

    $rendered_warehouses = [];
    foreach ($warehouses as $id => $location) {
        $rendered_warehouses[$location[0]][$location[1]] = $id;
    }

    for ($x = 0; $x < 600; $x++) {
        echo '<tr>' . PHP_EOL;
        for ($y = 0; $y < 400; $y++) {
            $code = '&#9632;';
            if (isset($rendered_warehouses[$x][$y])) {
                $code = '<span class="warehouse">&#8962;</span>';
            }
            echo '<td title="' . $x . ',' . $y . '">' . $code . '</td>' . PHP_EOL;
        }
        echo '</tr>' . PHP_EOL;
    }
    ?>
</table>
</body>
</html>