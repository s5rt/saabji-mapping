<?php
ini_set('display_errors', 0);
error_reporting(E_ALL);
header('Content-Type: application/json');
try {
    $dir = __DIR__ . '/data-csv';
    $file = $dir . '/alldata.csv';
    if (!is_dir($dir)) {
        mkdir($dir, 0777, true);
    }
    $headers = [
        "spot_time",
        "fid",
        "latitude",
        "longitude",
        "tree_id",
        "common_name",
        "scientific_name",
        "synonyms",
        "family",
        "plant_type",
        "leaf_characteristics",
        "phenology",
        "type",
        "condition",
        "growth_stage",
        "road_width_m",
        "height_m",
        "width_m"
    ];
    if (!file_exists($file)) {
        $fp = fopen($file, 'w');
        fputcsv($fp, $headers);
        fclose($fp);
    }
    $raw = file_get_contents('php://input');
    $input = json_decode($raw, true);
    if (!is_array($input)) {
        throw new Exception('Invalid JSON received');
    }
    $fid = 1;
    if (($fp = fopen($file, 'r')) !== false) {
        fgetcsv($fp);
        while (($row = fgetcsv($fp)) !== false) {
            if (isset($row[0]) && is_numeric($row[0])) {
                $fid = max($fid, ((int) $row[0]) + 1);
            }
        }
        fclose($fp);
    }
    $row = [
        date('Y-m-d H:i:s'),
        $fid,
        $input['latitude'] ?? '',
        $input['longitude'] ?? '',
        $input['tree_id'] ?? '',
        $input['common_name'] ?? '',
        '',
        '',
        '',
        'tree',
        '',
        '',
        '',
        $input['condition'] ?? '',
        $input['growth_stage'] ?? '',
        24,
        $input['height_m'] ?? '',
        $input['width_m'] ?? ''
    ];
    $fp = fopen($file, 'a');
    if (!$fp) {
        throw new Exception('Cannot open CSV file');
    }
    fputcsv($fp, $row);
    fclose($fp);
    echo json_encode([
        'status' => 'success',
        'fid' => $fid
    ]);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>