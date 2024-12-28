<?php
function generateInput($type, $name, $label, $value = '', $required = true, $options = []) {
    $id = $options['id'] ?? $name;
    $class = $options['class'] ?? 'form-control';
    $hint = $options['hint'] ?? '';
    
    $html = '<div class="mb-3">';
    $html .= '<label for="' . $id . '" class="form-label">' . $label . '</label>';
    $html .= '<input type="' . $type . '" class="' . $class . '" id="' . $id . '" name="' . $name . '" ';
    $html .= 'value="' . htmlspecialchars($value) . '" ';
    $html .= $required ? 'required' : '';
    $html .= '>';
    
    if (!empty($hint)) {
        $html .= '<small class="form-text text-muted">' . $hint . '</small>';
    }
    
    $html .= '</div>';
    return $html;
}
