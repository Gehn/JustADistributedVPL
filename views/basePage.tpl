<!DOCTYPE html>
<html>
	<head>
		<link href='http://fonts.googleapis.com/css?family=Michroma' rel='stylesheet' type='text/css'>
		
		<link rel="stylesheet" type="text/css" href="joint.css" />

		<script src="jquery.js"></script>
		<script src="lodash.js"></script>
		<script src="backbone.js"></script>
		<script src="joint.js"></script>


		<style>
			.title
			{
				font-family: 'Michroma', sans-serif;
				position:absolute;
				top:10px;
				left:240px;
				font-weight:bold;
				font-size:350%;
				text-decoration:none;
				color:#000;
				white-space:nowrap;
			}
			.subTitle
			{
				font-family: 'Michroma', sans-serif;
				position:absolute;
				top:62px;
				left:346px;
				font-weight:bold;
				font-size:250%;
				text-decoration:none;
				color:#000;
				white-space:nowrap;

			}

			.articleTitle
			{
				font-family: 'Michroma', sans-serif;
				font-weight:bold;
				font-size:140%;
			}
			.content
			{
				font-family: 'Michroma', sans-serif;
				position:absolute;
				top:200px;
				left:240px;
				margin-right:50px;
			}

			.index
			{
				position:fixed;
				top:150px;
				left:40px;
				border-right: 1px solid #bbb;
				width:170px;

			}
			.indexTitle
			{
				font-family: 'Michroma', sans-serif;
				font-weight:bold;
				font-size:140%;
				text-decoration:none;
				color:#000;
			}
			.indexEntry
			{
				font-family: 'Michroma', sans-serif;
				font-size:100%;
				color:#000;
				word-wrap: break-word;
			}
			.tab
			{
				padding-left:5em
			}
			.contentHeader
			{
				font-weight:bold;
			}

			#paper {
				 position: relative;
				 border: 1px solid gray;
				 display: inline-block;
				 background: transparent;
				 overflow: hidden;
			}
			#paper svg {
				 background: transparent;
			}
			#paper svg .link {
				 z-index: 2;
			}
			.html-element {
				 position: absolute;
				 background: transparent;
				 /* Make sure events are propagated to the JointJS element so, e.g. dragging works.*/
				 pointer-events: none;
				 -webkit-user-select: none;
				 border-radius: 4px;
				 box-shadow: inset 0 0 5px black, 2px 2px 1px gray;
				 padding: 5px;
				 box-sizing: border-box;
				 z-index: 2;
			}
			.html-element input,
			.html-element button {
				 /* Enable interacting with inputs only. */
				 pointer-events: auto;	 
			}
			.html-element button.delete {
				 color: white;
				 border: none;
				 background-color: #C0392B;
				 border-radius: 20px;
				 width: 15px;
				 height: 15px;
				 line-height: 15px;
				 text-align: middle;
				 position: absolute;
				 top: -15px;
				 left: -15px;
				 padding: 0;
				 margin: 0;
				 font-weight: bold;
				 cursor: pointer;
			}
			.html-element button.run {
				 color: white;
				 border: none;
				 background-color: #7CFC00;
				 border-radius: 20px;
				 width: 15px;
				 height: 15px;
				 line-height: 15px;
				 text-align: middle;
				 position: absolute;
				 top: -15px;
				 left: -15px;
				 padding: 0;
				 margin: 0;
				 font-weight: bold;
				 cursor: pointer;
			}
			.html-element button.delete:hover {
				 width: 20px;
				 height: 20px;
				 line-height: 20px;
			}
			.html-element button.run:hover {
				 width: 20px;
				 height: 20px;
				 line-height: 20px;
			}
			.html-element label {
				text-shadow: 1px 0 0 black;
				font-weight: bold;
				font-size: 10px;
			}
			.html-element label.contrast {
				color: white;
			}
			.html-element span {
				 position: absolute;
				 top: 2px;
				 right: 9px;
				 color: transparent;
				 font-size: 10px;
			}
		</style>
	</head>
	<body>
		<a class="title" href=#>ControlFlow</a>
		<a class="subTitle" href=#>V0.1</a>
		<div class="index">
			<a class="indexTitle">Link Type</a> <br>
			<select class="linkType">
			</select>
			<a class="indexTitle" href=/>Available States</a> <br>
		</div>
		<div class="content" id="stateMachineWindow">
		</div>
		<script>

			var states = {}

			var graph = new joint.dia.Graph;
			var paper = new joint.dia.Paper({
			    el: $('#stateMachineWindow'),
			    model: graph,
			    gridSize: 1
			});

			// Thanks/Credit to jointJS for the framework of embedded elements, and the
			// embedding callback logic used below.

			// Create a custom element.
			// ------------------------
			
			joint.shapes.html = {};
			joint.shapes.html.Element = joint.shapes.basic.Rect.extend({
				defaults: joint.util.deepSupplement({
					type: 'html.Element',
					attrs: {
						rect: { stroke: 'none', 'fill-opacity': 0 }
					}
				}, joint.shapes.basic.Rect.prototype.defaults)
			});
			
			// Create a custom view for that element that displays an HTML div above it.
			// -------------------------------------------------------------------------
			
			joint.shapes.html.ElementView = joint.dia.ElementView.extend({
			
				template: [
					'<div class="html-element">',
					'<button class="delete">x</button>',
					'<button class="run">o</button>',
					'<label></label>',
					'<span></span>', '<br/>',
					'</div>'
				].join(''),
			
				initialize: function() {
					_.bindAll(this, 'updateBox');
					joint.dia.ElementView.prototype.initialize.apply(this, arguments);
			
					var bbox = this.model.getBBox();
					this.$box = $(_.template(this.template)());
//					this.$box.find('.delete').on('click', _.bind(this.model.remove, this.model));
					this.$box.find('.delete').on('click', _.bind(RemoveState, this, this.model.state));
					this.$box.find('.run').on('click', _.bind(RunState, this, this.model.state));
					this.$box.find('.run').parentElement = this;
					this.$box.find('.run').css({left: bbox.width});
					// Update the box position whenever the underlying model changes.
					this.model.on('change', this.updateBox, this);
					// Remove the box when the model gets removed from the graph.
					this.model.on('remove', this.removeBox, this);

//					this.model.on('remove', RemoveStateViaEvent, this, this.model.state.stateId);
			
					this.updateBox();
				},
				render: function() {
					joint.dia.ElementView.prototype.render.apply(this, arguments);
					this.paper.$el.prepend(this.$box);
					this.updateBox();
					return this;
				},
				updateBox: function() {
					// Set the position and dimension of the box so that it covers the JointJS element.
					var bbox = this.model.getBBox();
					// Example of updating the HTML with a data stored in the cell model.
					this.$box.find('label').text(this.model.get('label'));
					this.$box.find('span').text(this.model.get('select'));
					this.$box.css({ width: bbox.width, height: bbox.height, left: bbox.x, top: bbox.y, transform: 'rotate(' + (this.model.get('angle') || 0) + 'deg)', background: this.model.get('background'), 'z-index':0});
				},
				removeBox: function(evt) {
					this.$box.remove();
				}
			});

			// Create a custom element.
			// ------------------------
			
			joint.shapes.htmlarg = {};
			joint.shapes.htmlarg.Element = joint.shapes.basic.Rect.extend({
				defaults: joint.util.deepSupplement({
					type: 'htmlarg.Element',
					attrs: {
						rect: { stroke: 'none', 'fill-opacity': 0 }
					}
				}, joint.shapes.basic.Rect.prototype.defaults)
			});
			
			// Create a custom view for that element that displays an HTML div above it.
			// -------------------------------------------------------------------------
			
			joint.shapes.htmlarg.ElementView = joint.dia.ElementView.extend({
			
				template: [
					'<div class="html-element">',
					'<label class="contrast"></label>',
					'<span></span>', '<br/>',
					'<input type="text" value="" style="width: 80px"/>',
					'</div>'
				].join(''),
			
				initialize: function() {
					//TODO: replace all the _bind with this.  Much cleaner.
					var argCell = this.model;

					_.bindAll(this, 'updateBox');
					joint.dia.ElementView.prototype.initialize.apply(this, arguments);
			
					this.$box = $(_.template(this.template)());
					// Update the box position whenever the underlying model changes.
					this.model.on('change', this.updateBox, this);
					// Remove the box when the model gets removed from the graph.
					this.model.on('remove', this.removeBox, this);

				        this.$box.find('input,select').on('mousedown click', function(evt) { evt.stopPropagation(); });
					this.$box.find('input').keyup(function(e) {
									if (e.keyCode == 13) {
										PrepareArgument(argCell);
									}
					});
					// Proliferate input change to the cell.
				        this.$box.find('input').on('change', _.bind(function(evt) {
				            this.model.set('input', $(evt.target).val());
				        }, this));
					this.updateBox();
				},
				render: function() {
					joint.dia.ElementView.prototype.render.apply(this, arguments);
					this.paper.$el.prepend(this.$box);
					this.updateBox();
					return this;
				},
				updateBox: function() {
					// Set the position and dimension of the box so that it covers the JointJS element.
					var bbox = this.model.getBBox();
					// Example of updating the HTML with a data stored in the cell model.
					this.$box.find('label').text(this.model.get('label'));
					this.$box.find('input').val(this.model.get('input'));
					this.$box.find('span').text(this.model.get('select'));
					this.$box.css({ width: bbox.width, height: bbox.height, left: bbox.x, top: bbox.y, transform: 'rotate(' + (this.model.get('angle') || 0) + 'deg)', background: this.model.get('background'), 'z-index':1});
				},
				removeBox: function(evt) {
					this.$box.remove();
				}
			});



			function JoinStates(sourceState, targetState, innerCell, linkType)
			{
				var urlArg = "";
				var urlSetting = ""
				if (innerCell != undefined)
				{
					if (innerCell.argumentText != undefined)
					{
						urlArg = '&argument=' + innerCell.argumentText;
					}
					else if (innerCell.settingText != undefined)
					{
						urlSetting = '&setting=' + innerCell.settingText;
					}
				}

				linkTypeArg = "";
				if (linkType != undefined)
				{
					linkTypeArg = '&linkType=' + linkType;
				}

				$.ajax({
					url: '/LinkStates?parentStateId=' + sourceState.stateId + '&childStateId=' + targetState.stateId + urlArg + linkTypeArg + urlSetting,
					type: 'PUT',
					success: function() {
							ConfirmJoinStates(sourceState, targetState, innerCell, linkType);
					}
				});
			}

			function ConfirmJoinStates(sourceState, targetState, innerCell, linkType)
			{
				var sourceId = sourceState.cell.id;
				var targetId = targetState.cell.id;
				if (innerCell)
				{
					targetId = innerCell.id;
				}

				var newLink = new joint.dia.Link({
					source: { id: sourceId },
					target: { id: targetId }
				});
				newLink.attr({
					'.marker-target': { fill: 'black', d: 'M 10 0 L 0 5 L 10 10 z' }
				});
				if (linkType == "optional")
				{
					newLink.linkType = linkType;
					newLink.attr({
						'.connection': { 'stroke-dasharray': '2,5' }
					});
				}
				graph.addCells([newLink]);
			};


			var potentialLinkSource = null;
			function StartJoiningStates(sourceState)
			{
				potentialLinkSource = sourceState;
			}

			function FinishJoiningStates(targetState, innerCell)
			{
				var temp = potentialLinkSource;
				potentialLinkSource = null;
				JoinStates(temp, targetState, innerCell, $('select.linkType').val());
			}

			function IsAlreadyJoiningStates()
			{
				return (potentialLinkSource != null);
			}

			function UnlinkStates(sourceState, targetState, innerCell, linkType)
			{
				var urlArg = "";
				var urlSetting = "";
				if (innerCell != undefined)
				{
					if (innerCell.argumentText != undefined)
					{
						var argumentName = innerCell.argumentText;
						//var argumentName = argumentCell.attributes.label;
						urlArg = '&argument=' + argumentName;
					}
					else if (innerCell.settingText != undefined)
					{
						urlSetting = '&setting=' + innerCell.settingName;
					}
				}


				$.ajax({
					url: '/UnlinkStates?parentStateId=' + sourceState.stateId + 
						'&childStateId=' + targetState.stateId + urlArg + urlSetting,
					type: 'PUT',
					success: function() {
					},
					error: function() {
						//On failure, we want to recreate the link we deleted.
						ConfirmJoinStates(sourceState, targetState, innerCell, linkType)
					}
				});

			}

			function NewState(stateTypeId)
			{
				if (stateTypeId != "remote")
				{
					$.ajax({
						url: '/AddState?stateTypeId=' + encodeURIComponent(stateTypeId),
						type: 'PUT',
						success: function(response) { 
							ConfirmNewState(response['stateId'], 
								stateTypeId, 
								response['args'], 
								response['settings'],
								response['remoteId'],
								response['remoteUri'],
								response['populatedArgs'], 
								response['populatedSettings']); 
						}
					});
				} else {
					NewRemoteState(stateTypeId);
				}
			}

			function NewRemoteState(stateTypeId)
			{
				var remoteUri = prompt("Enter target URI:", "192.168.1.10:99");
				if (remoteUri != null)
				{
					//TODO: replace this with an embedded graph in a lightbox.
					var remoteId = prompt("Enter target state ID", "2");
					if (remoteId != null)
					{
						$.ajax({
							url: '/AddRemoteState?remoteIp=' + 
								encodeURIComponent(remoteUri) + 
								'&remoteStateId=' + 
								remoteId,
							type: 'PUT',
							success: function(addResponse) { 
						
								ConfirmNewState(addResponse['stateId'], 
									getResponse['typeId'], 
									getResponse['args'], 
									getResponse['settings'],
									remoteId,
									remoteUri,
									getResponse['populatedArgs'],
									getResponse['populatedSettings']); 
							}
						}); 
					}
				}
			}
			

			function ConfirmNewState(stateId, 
					stateTypeId, 
					stateArgs, 
					stateSettings, 
					remoteStateId, 
					remoteStateUri,
					populatedArgs,
					populatedSettings)
			{
				var cellFill = 'white'
				var cellLabel = stateTypeId
				if (remoteStateId != undefined)
				{
					cellLabel = remoteStateUri + "-" + stateTypeId
					cellFill = 'grey'
				}
				// Make the cell for the state.
				var cellWidth = 100 + 100 * Math.max(stateArgs.length, stateSettings.length);
				var newCell = new joint.shapes.html.Element({
		                        position: { x: 100, y: 30 },
	        	                size: { width: cellWidth, height: 30 },
               	        	   	attrs: { 
						rect: { 
							fill: 'green'
						}, 
						text: { 
							text: "", 
							fill: 'black',
						}
					},
					label: cellLabel,
					background: cellFill
        	                });
				//newCell.stateId = stateId;
				newCell.state = {cell:newCell, 
							stateId:stateId,
							stateTypeId:stateTypeId,
							stateArgs:stateArgs,
							stateSettings:stateSettings,
							remoteStateId:remoteStateId,
							remoteStateUri:remoteStateUri
						};

				graph.addCells([newCell]);
				//states[stateId] = newCell;
				states[stateId] = newCell.state

				// Make nested cells to represent the arguments.
				var verticalPosition = 0;
				var horizontalPosition = 0;
				if (stateSettings.length > 0)
				{
					verticalPosition += 60;
				}
				stateSettings.map( function(setting)
				{
					var populatedSetting = undefined;
					if (populatedSettings)
					{
						populatedSetting = populatedSettings[setting];
					}

					var newSetting = new joint.shapes.htmlarg.Element({
			                        position: { x: 100 + 100 * horizontalPosition, y: verticalPosition },
		        	                size: { width: 100, height: 60 },
						label: setting,
						background: 'grey',
						input: populatedSetting,
        		                });
					//TODO: instead of this argumentText/settingText nonsense, have name and type.
					newSetting.settingText = setting;
					horizontalPosition++;
					newCell.embed(newSetting);
					graph.addCells([newSetting]);
				});
				horizontalPosition = 0;
				if (stateArgs.length > 0)
				{
					verticalPosition += 60;
				}
				stateArgs.map( function(argument)
				{
					var populatedArg = undefined;
					if (populatedArgs)
					{
						populatedArg = populatedArgs[argument];
					}

					var newArg = new joint.shapes.htmlarg.Element({
			                        position: { x: 100 + 100 * horizontalPosition, y: verticalPosition },
		        	                size: { width: 100, height: 60 },
						label: argument,
						background: 'black',
						input: populatedArg,
        		                });
					newArg.argumentText = argument;
					horizontalPosition++;
					newCell.embed(newArg);
					graph.addCells([newArg]);
				});
				newCell.resize(cellWidth, verticalPosition+30);

				return newCell.state;
			}

			function RemoveState(state)
			{
				$.ajax({
					url: '/RemoveState?stateId=' + state.stateId,
					type: 'PUT',
					success: function(response) {
						ConfirmRemoveState(state);
					}
				});
			}

			function ConfirmRemoveState(state)
			{
				state.cell.remove();
			}

			function RunStateMachine()
			{
				$.ajax({
					url: '/Run',
					type: 'PUT',
					success: function(response) {
						return;
					}
				});
			}

			function RunState(state)
			{
				$.ajax({
					url: '/Run?stateId=' + state.stateId,
					type: 'PUT',
					success: function(response) {
						return;
					}
				});
			}

			function PrepareArgument(argumentCell)
			{
				var inputName = undefined;
				var inputTypeQuery = undefined;
				if (argumentCell.argumentText != undefined)
				{
					inputName = argumentCell.argumentText;
					inputTypeQuery = "/PrepareArgument";
				}
				else
				{
					inputName = argumentCell.settingText;
					inputTypeQuery = "/PrepareSetting";
				}

				var input = argumentCell.attributes.input;
				var parentId = argumentCell.get('parent');

				if (parentId)
				{
					var state = graph.getCell(parentId).state;
					$.ajax({
						url: inputTypeQuery + '?stateId=' + state.stateId + '&position=' + inputName + '&value=' + input,
						type: 'PUT',
						success: function(response) {
							ConfirmPrepareArgument(argumentCell, input);
						},
						error: function(response) {
							//TODO: make this replace with the last viable input
							ConfirmPrepareArgument(argumentCell, "");
						}
					});
				}

			}

			function ConfirmPrepareArgument(argumentCell, argument)
			{
				argumentCell.attributes.input = argument;
			}

			function LoadStateMachine()
			{
				$.ajax({
					url: '/GetStateGraph',
					type: 'GET',
					success: function(response) { 
						ConfirmLoadingStateMachine(response); 
					}
				});
			
			}

			function ConfirmLoadingStateMachine(rawStates)
			{
				for (var stateId in rawStates)
				{
					var rawState = rawStates[stateId];

					var stateType = rawState['typeId'];
					var args = rawState['args'];
					var settings = rawState['settings'];
					var populatedArgs = rawState['populatedArgs'];
					var populatedSettings = rawState['populatedSettings'];
					var remoteId = undefined;
					var remoteUri = undefined;
					if( 'remoteId' in rawState)
					{
						remoteId = rawState['remoteId'];
						remoteUri = rawState['remoteUri'];
					}
					var newState = ConfirmNewState(stateId, stateType, args, settings, remoteId, remoteUri, populatedArgs, populatedSettings);

					var position = rawState['arbitraryData']['position'];
					if (position != undefined)
					{
						position = JSON.parse(position);
						newState.cell.translate(position['x']-100, position['y']-50);
					}
				
				}
				// Yes I'm looping it twice; you could technically create the parent if it doesn't
				// exist and then do this in the main loop, but in the interest of not prematurely optimizing
				// doing the far more logically concise all states -> all vectors creation.
				for (var stateId in rawStates)
				{
					var incomingLinks = rawStates[stateId]['incomingLinks'];
					for (var incomingLinkId in incomingLinks)
					{
						var incomingLink = incomingLinks[incomingLinkId];

						var sourceId = incomingLink["parent"];
						var linkType = incomingLink["linkType"];
						var argument = incomingLink["argument"];
						var setting = incomingLink["setting"];

						var source = states[sourceId];
						var target = states[stateId];

						var innerCell = undefined;
						var innerCellList = [];
						if (argument != undefined)
						{
							innerCellList = target.cell.getEmbeddedCells().filter( 
								function(element) { return element.argumentText == argument });
						}
						else if (setting != undefined)
						{
							innerCellList = target.cell.getEmbeddedCells().filter( 
								function(element) { return element.settingText == setting });
						}
						if (innerCellList != [])
						{
							innerCell = innerCellList[0];
						}
						ConfirmJoinStates(source, target, innerCell, linkType);
					}
				}
			}

			function LoadAvailableLinkTypes()
			{
				$.ajax({
					url: '/GetAvailableLinkTypes',
					type: 'GET',
					success: function(response) { 
						ConfirmLoadAvailableLinkTypes(response); 
					}
				});
			}

			function ConfirmLoadAvailableLinkTypes(availableLinkTypes)
			{
				$("option.linkType").remove();

				var targetDiv = $("select.linkType");

				for (var linkType in availableLinkTypes)
				{
					var newLinkTypeOptionTag = document.createElement('option');
					newLinkTypeOptionTag.setAttribute("class", "linkType");
					newLinkTypeOptionTag.setAttribute("value", linkType);
					newLinkTypeOptionTag.innerText = linkType;

					targetDiv.append(newLinkTypeOptionTag);
				}
			}

			function LoadAvailableStateTypes()
			{
				$.ajax({
					url: '/GetAvailableStateTypes',
					type: 'GET',
					success: function(response) { 
						ConfirmLoadAvailableStateTypes(response); 
					}
				});
			}

			function ConfirmLoadAvailableStateTypes(availableStateTypes)
			{
				$("a.indexEntry").remove();

				var targetDiv = $("div.index");
				// TODO: totally wack that this is built into the web client.  Fix that...
				targetDiv.append('<a class="indexEntry" href=# stateTypeId="remote">Import Remote State</a> <br>');

				for (var stateType in availableStateTypes)
				{
					var stateTypeShortName = availableStateTypes[stateType];

//					TODO: This is way more concise, but my intuition is there's something dangerous in it.
//					$("div.index").append($('<a class="indexEntry" href=# stateTypeId=' + stateType + '>' + stateTypeShortName + '</a> <br>'));

					var newStateTypeATag = document.createElement('a');
					newStateTypeATag.setAttribute("class", "indexEntry");
					newStateTypeATag.setAttribute("href", "#");
					newStateTypeATag.setAttribute("stateTypeId", stateType);
					newStateTypeATag.innerText = stateTypeShortName;
					var breakTag = document.createElement('br');

					targetDiv.append(newStateTypeATag);
					targetDiv.append(breakTag);
				}

				// Set up the on click handler  TODO: do this as onclick?
				$('a.indexEntry').click( function(e) {
					var stateTypeId = e.target.attributes.stateTypeId.value;
					NewState(stateTypeId);
				});
			}


			function SetArbitraryData(stateId, key, value)
			{
				$.ajax({
					url: '/SetArbitraryData?&stateId=' + stateId + "&key=" + key + "&value=" + value,
					type: 'Put',
					success: function(response) { 
						ConfirmLoadingStateMachine(response); 
					}
				});
			
			}


			function GetArbitraryData(stateId, key)
			{
				$.ajax({
					url: '/GetArbitraryData?&stateId=' + stateId + "&value=" + value,
					type: 'GET',
					success: function(response) {
						ConfirmLoadingStateMachine(response);
					}
				});
			
			}


			paper.on('cell:pointerdblclick', function(cellView, evt, x, y) {
				var targetCell = cellView.model;
				var targetInnerCell = undefined;
				var parentId = targetCell.get('parent');
				if (parentId)
				{
					targetInnerCell = targetCell
					targetCell = graph.getCell(parentId);
				}

				if (!IsAlreadyJoiningStates())
				{
					StartJoiningStates(targetCell.state);
				}
				else
				{
					FinishJoiningStates(targetCell.state, targetInnerCell);
				}
			});


			paper.on('cell:pointerup', function(cellView, evt, x, y) {
				var cell = cellView.model;
				var parentId = cell.get('parent');
				if (!parentId) 
				{
					SetArbitraryData(cell.state.stateId, "position", JSON.stringify(cell.position()));
				}
			});
			
			//		ON PARENT SIZE CHANGE LOGIC FOR EMBEDDING
			graph.on('change:size', function(cell, newPosition, opt) {
				
				if (opt.skipParentHandler) return;
				
				if (cell.get('embeds') && cell.get('embeds').length) {
					// If we're manipulating a parent element, let's store
					// it's original size to a special property so that
					// we can shrink the parent element back while manipulating
					// its children.
					cell.set('originalSize', cell.get('size'));
				}
			});
			

			//		ON CHILD MOVEMENT LOGIC FOR EMBEDDING
			graph.on('change:position', function(cell, newPosition, opt) 
			{
		
				if (opt.skipParentHandler) return;
		
				if (cell.get('embeds') && cell.get('embeds').length) {
					// If we're manipulating a parent element, let's store
					// it's original position to a special property so that
					// we can shrink the parent element back while manipulating
					// its children.
					cell.set('originalPosition', cell.get('position'));
				}
				
				var parentId = cell.get('parent');
				if (!parentId) 
				{
					return;
				}
		
				var parent = graph.getCell(parentId);
				var parentBbox = parent.getBBox();
		
				if (!parent.get('originalPosition')) parent.set('originalPosition', parent.get('position'));
				if (!parent.get('originalSize')) parent.set('originalSize', parent.get('size'));
				
				var originalPosition = parent.get('originalPosition');
				var originalSize = parent.get('originalSize');
				
				var newX = originalPosition.x;
				var newY = originalPosition.y;
				var newCornerX = originalPosition.x + originalSize.width;
				var newCornerY = originalPosition.y + originalSize.height;
				
				_.each(parent.getEmbeddedCells(), function(child) {
		
					var childBbox = child.getBBox();
					
					if (childBbox.x < newX) { newX = childBbox.x; }
					if (childBbox.y < newY) { newY = childBbox.y; }
					if (childBbox.corner().x > newCornerX) { newCornerX = childBbox.corner().x; }
					if (childBbox.corner().y > newCornerY) { newCornerY = childBbox.corner().y; }
				});
		
				// Note that we also pass a flag so that we know we shouldn't adjust the
				// `originalPosition` and `originalSize` in our handlers as a reaction
				// on the following `set()` call.
				parent.set({
					position: { x: newX, y: newY },
					size: { width: newCornerX - newX, height: newCornerY - newY }
				}, { skipParentHandler: true });
			});
			

			//		ELEMENT DELETION LOGIC
			// TODO: need to figure out how to only trigger on user click, otherwise the engine handles link deletion.
			graph.on('remove', function(cell, collection, opt)
			{
				if (cell.isLink())
				{
					var sourceCell = graph.getCell(cell.attributes.source.id);
					var targetCell = graph.getCell(cell.attributes.target.id);


					var targetArgumentCell = undefined;
					var parentId = targetCell.get('parent');
					if (parentId)
					{
						targetArgumentCell = targetCell;
						targetCell = graph.getCell(parentId);
					}

					// Incomplete link.  This only works sometimes, depending on how the removal callbacks are ordered.
					// TODO: make it work more of the time, relying on idempotency seems sloppy.
					if (sourceCell == undefined 
						|| targetCell == undefined
						|| sourceCell.state == undefined
						|| targetCell.state == undefined
						|| !states.hasOwnProperty(sourceCell.state.stateId)
						|| !states.hasOwnProperty(targetCell.state.stateId))
					{
						return
					}

					UnlinkStates(sourceCell.state, targetCell.state, targetArgumentCell, cell.linkType);
				}
			})

			// Keep expanding the paper as people scroll down.  
			// TODO: In the future I may want to only do this if there is a cell "near" the bottom, / let it contract.
			$(window).on('scroll', function(){
				if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10 ) {
					paper.setDimensions(paper.width, $(window).height() + $(window).scrollTop())
				}					
			}).scroll();

			LoadStateMachine();
			LoadAvailableStateTypes();
			LoadAvailableLinkTypes();
	
		</script>
	</body>
</html>
