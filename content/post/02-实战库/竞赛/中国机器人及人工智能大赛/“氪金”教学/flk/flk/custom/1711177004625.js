Blockly.Blocks['1711177004625'] = {
  init: function() {
    this.jsonInit({
      "type": "1711177004625",
      "message0": "text",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711177004625'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(70,29,190,100,93,55,124,100,127,174,10,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(70,29,190,100,93,55,124,100,127,174,10,98,106,145,81,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(69,28,189,94,116,150,37,99,127,174,10,98,106,145,81,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(70,29,190,98,160,150,100,104,127,174,10,98,110,156,65,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(70,29,190,96,153,50,187,88,127,174,10,98,110,156,65,88,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(70,29,190,95,157,48,190,91,127,174,10,99,125,155,89,92,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(70,29,190,95,160,56,190,101,127,174,10,95,134,154,95,101,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(70,29,190,95,160,107,141,101,127,174,10,95,137,153,57,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(70,29,190,99,160,10,187,109,127,174,10,99,65,163,29,96,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711177004625'] = function(block) {
  let code = "robot.leju_action('text')\n";
  return code;
}

