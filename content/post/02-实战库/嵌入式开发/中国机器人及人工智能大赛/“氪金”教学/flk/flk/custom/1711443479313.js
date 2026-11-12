Blockly.Blocks['1711443479313'] = {
  init: function() {
    this.jsonInit({
      "type": "1711443479313",
      "message0": "box_Lturn_dg",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711443479313'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,100,137,190,37,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,105,89,81,84,101,137,190,37,109,61,152,33,103,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,100,137,190,37,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711443479313'] = function(block) {
  let code = "robot.leju_action('box_Lturn_dg')\n";
  return code;
}

