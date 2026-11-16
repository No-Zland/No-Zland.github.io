Blockly.Blocks['1710681399069'] = {
  init: function() {
    this.jsonInit({
      "type": "1710681399069",
      "message0": "左转30度pro",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710681399069'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(41,37,172,100,50,49,94,96,154,178,35,103,94,182,22,101,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,99,89,23,145,100,155,178,35,98,111,182,51,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710681399069'] = function(block) {
  let code = "robot.leju_action('左转30度pro')\n";
  return code;
}

