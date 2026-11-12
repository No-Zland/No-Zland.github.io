Blockly.Blocks['1711510087314'] = {
  init: function() {
    this.jsonInit({
      "type": "1711510087314",
      "message0": "游泳准备动作",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711510087314'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(20)\nMOTOmove19(66,26,190,52,152,150,56,60,130,176,10,140,40,50,139,140,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(67,27,161,52,152,150,56,60,128,178,40,140,40,50,139,140,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(67,27,161,56,119,103,52,69,128,178,40,136,100,116,147,127,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(67,27,161,77,119,105,70,77,128,178,40,129,99,115,131,128,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(67,27,161,100,93,55,124,100,128,178,40,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711510087314'] = function(block) {
  let code = "robot.leju_action('游泳准备动作')\n";
  return code;
}

