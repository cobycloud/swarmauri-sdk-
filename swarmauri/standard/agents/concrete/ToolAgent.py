from typing import Any, Optional, Union, Dict, Literal
import json
from pydantic import ConfigDict
from swarmauri.core.messages import IMessage

from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.agents.base.AgentBase import AgentBase
from swarmauri.standard.agents.base.AgentConversationMixin import AgentConversationMixin
from swarmauri.standard.agents.base.AgentToolMixin import AgentToolMixin
from swarmauri.standard.messages.concrete import HumanMessage, AgentMessage, FunctionMessage

from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.toolkits.concrete.Toolkit import Toolkit
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class ToolAgent(AgentToolMixin, AgentConversationMixin, AgentBase):
    llm: SubclassUnion[LLMBase]
    toolkit: SubclassUnion[Toolkit]
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ToolAgent'] = 'ToolAgent'
    
    def exec(self, 
        input_data: Optional[Union[str, IMessage]] = "",  
        llm_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.conversation
        llm = self.llm
        toolkit = self.toolkit

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(content=input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        conversation.add_message(human_message)

        #predict a response        
        prediction = llm.predict(messages=conversation.history, 
                                   toolkit=toolkit, 
                                   tool_choice="auto", 
                                   **llm_kwargs)
        
        prediction_message = prediction.choices[0].message
        
        agent_response = prediction_message.content
        
        agent_message = AgentMessage(content=prediction_message, 
                                     tool_calls=prediction_message.tool_calls)
        conversation.add_message(agent_message)
        
        tool_calls = prediction.choices[0].message.tool_calls
        if tool_calls:
        
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                func_call = toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                
                func_message = FunctionMessage(content=func_result, 
                                               name=func_name, 
                                               tool_call_id=tool_call.id)
                conversation.add_message(func_message)
            
            
            rag_prediction = llm.predict(messages=conversation.history, 
                                           toolkit=toolkit, 
                                           tool_choice="none",
                                           **llm_kwargs)
            
            prediction_message = rag_prediction.choices[0].message
            
            agent_response = prediction_message.content
            agent_message = AgentMessage(content=agent_response)
            conversation.add_message(agent_message)
            prediction = rag_prediction
            
        return agent_response 