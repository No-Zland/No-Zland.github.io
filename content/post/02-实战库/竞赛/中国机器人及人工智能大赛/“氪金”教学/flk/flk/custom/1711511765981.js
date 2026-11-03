Blockly.Blocks['1711511765981'] = {
  init: function() {
    this.jsonInit({
      "type": "1711511765981",
      "message0": "游泳右转1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711511765981'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(80,103,107,98,107,54,119,91,121,83,105,145,112,164,103,97,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,103,107,100,113,70,123,94,121,83,105,98,106,178,71,103,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711511765981'] = function(block) {
  let code = "robot.leju_action('游泳右转1')\n";
  return code;
}

