Blockly.Blocks['1711169628738'] = {
  init: function() {
    this.jsonInit({
      "type": "1711169628738",
      "message0": "box_double_up_x",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711169628738'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(20)\nMOTOmove19(71,72,177,62,156,150,55,68,114,141,25,136,40,50,144,131,128,71,99)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(71,72,177,38,156,140,46,61,114,141,25,158,42,58,155,140,128,71,99)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(91,13,177,38,156,140,46,61,106,190,19,158,42,58,155,140,128,71,99)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(91,13,177,54,143,150,68,60,106,190,19,144,41,50,121,140,128,71,99)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(67,26,190,100,93,55,124,100,129,176,10,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711169628738'] = function(block) {
  let code = "robot.leju_action('box_double_up_x')\n";
  return code;
}

