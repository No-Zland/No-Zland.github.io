Blockly.Blocks['1711442483222'] = {
  init: function() {
    this.jsonInit({
      "type": "1711442483222",
      "message0": "box-Rmove-dg",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711442483222'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,10,163,100,93,55,124,100,138,188,37,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(64,10,163,53,102,40,148,81,138,188,37,115,85,130,77,136,120,40,100)\nMOTOwait()\nMOTOsetspeed(130)\nMOTOmove19(64,10,163,93,113,70,123,94,138,188,37,102,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(64,10,163,100,113,70,123,98,138,188,37,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711442483222'] = function(block) {
  let code = "robot.leju_action('box-Rmove-dg')\n";
  return code;
}

