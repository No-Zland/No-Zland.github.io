Blockly.Blocks['1711515541618'] = {
  init: function() {
    this.jsonInit({
      "type": "1711515541618",
      "message0": "游泳左转5",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711515541618'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,100,113,70,123,98,122,84,176,99,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,52,83,40,81,80,122,84,176,115,85,130,77,136,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,93,113,70,123,94,122,84,176,102,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(81,109,17,100,113,70,123,98,122,84,176,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711515541618'] = function(block) {
  let code = "robot.leju_action('游泳左转5')\n";
  return code;
}

