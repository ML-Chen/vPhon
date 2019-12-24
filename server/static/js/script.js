"use strict";

function convert(input, callback) {
    $.get("/convert", {input}, callback);
}

function updateOutput(text) {
    console.log(text);
    $("input[name='output']").val(text);
}

function _convert() {
    convert({
        text: $("#input").val(),
        dialect: {
            'northern': 'n',
            'central': 'c',
            'southern': 's'
        }[$("input[name='dialect']:checked").val()],
        tones: {
            'tone-numerals': '',
            'tone-letters': 'tl',
            'tone-6': '6',
            'tone-8': '8'
        }[$("input[name='tone']:checked").val()],
        palatals: $("input[name='palatals']").is(':checked'),
        glottal: $("input[name='glottal']").is(':checked'),
        tokenize: $("input[name='tokenize']").is(':checked'),
        delimit: $("input[name='delimit']").val(),
    }, updateOutput)
}

$(document).ready(function() {
    $("#input").change(function() {
        $.when($(this).focusout()).then(function() {
            convert({
                text: $("#input").val(),
                dialect: '',
                tones: {
                    'tone-numerals': '',
                    'tone-letters': 'tl',
                    'tone-6': '6',
                    'tone-8': '8'
                    }[$("input[name='tone']:checked").val()],
                palatals: $("input[name='palatals']").is(':checked'),
                glottal: $("input[name='glottal']").is(':checked'),
                tokenize: $("input[name='tokenize']").is(':checked'),
                delimit: $("input[name='delimit']").val(),
            }, updateOutput)
        });
    });
})