Blockly.Blocks['1719143182488'] = {
  init: function() {
    this.jsonInit({
      "type": "1719143182488",
      "message0": "box-rturn-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1719143182488'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,10,179,105,89,81,84,101,137,190,23,109,61,152,33,103,120,40,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(64,10,179,100,93,55,124,100,137,190,23,100,107,145,76,100,120,40,100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1719143182488'] = function(block) {
  let code = "robot.leju_action('box-rturn-q')\n";
  return code;
}

