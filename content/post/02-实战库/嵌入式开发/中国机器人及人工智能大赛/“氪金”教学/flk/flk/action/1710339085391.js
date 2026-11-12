Blockly.Blocks['1710339085391'] = {
  init: function() {
    this.jsonInit({
      "type": "1710339085391",
      "message0": "抱块左转25度",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710339085391'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,100,61,42,94,98,154,178,35,98,84,190,18,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,99,89,23,145,100,155,178,35,98,111,182,51,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710339085391'] = function(block) {
  let code = "robot.leju_action('抱块左转25度')\n";
  return code;
}

