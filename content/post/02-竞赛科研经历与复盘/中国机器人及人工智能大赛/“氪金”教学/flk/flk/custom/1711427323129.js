Blockly.Blocks['1711427323129'] = {
  init: function() {
    this.jsonInit({
      "type": "1711427323129",
      "message0": "box-Lmove-max",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711427323129'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(67,25,180,100,93,55,124,100,136,176,22,99,107,144,75,99,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(67,25,180,75,109,78,117,69,136,176,22,144,85,117,82,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(67,25,180,93,113,70,123,94,136,176,22,102,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(67,25,180,96,113,70,123,94,136,176,22,95,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(67,25,180,100,113,70,123,94,136,176,22,98,87,132,76,104,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711427323129'] = function(block) {
  let code = "robot.leju_action('box-Lmove-max')\n";
  return code;
}

