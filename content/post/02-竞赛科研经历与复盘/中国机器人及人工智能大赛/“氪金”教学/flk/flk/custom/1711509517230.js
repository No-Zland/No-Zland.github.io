Blockly.Blocks['1711509517230'] = {
  init: function() {
    this.jsonInit({
      "type": "1711509517230",
      "message0": "游泳右转",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711509517230'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(108,102,36,74,109,76,116,69,120,75,171,145,95,114,132,96,128,71,100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(108,102,36,93,113,70,123,94,120,75,171,102,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(108,102,36,96,113,70,123,94,120,75,171,95,87,132,76,104,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711509517230'] = function(block) {
  let code = "robot.leju_action('游泳右转')\n";
  return code;
}

