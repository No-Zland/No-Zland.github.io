Blockly.Blocks['1711442077594'] = {
  init: function() {
    this.jsonInit({
      "type": "1711442077594",
      "message0": "box-up1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711442077594'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(130)\nMOTOmove19(78,56,100,101,113,63,128,95,115,152,101,100,86,133,74,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(70,62,162,53,154,150,59,62,127,143,45,140,40,50,137,140,128,71,100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(65,10,161,53,154,150,59,62,138,187,41,140,40,50,137,140,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,100,138,190,37,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711442077594'] = function(block) {
  let code = "robot.leju_action('box-up1')\n";
  return code;
}

