Blockly.Blocks['1711174241267'] = {
  init: function() {
    this.jsonInit({
      "type": "1711174241267",
      "message0": "x_dbbox_lturn",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711174241267'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,100,93,55,124,100,129,174,10,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,107,89,106,59,103,129,174,10,105,51,152,21,98,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,100,93,55,124,100,129,174,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711174241267'] = function(block) {
  let code = "robot.leju_action('x_dbbox_lturn')\n";
  return code;
}

