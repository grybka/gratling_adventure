from .Producer import Production,Grammar,GrammarWithMaxUsage,Symbol
#from Producer import Production,Grammar,GrammarWithMaxUsage,Symbol


def expand_list(orig_list,elem_num,new_options):
    #return a list of lists in which elem_num has been relpaced by one of the options
    ret=[]
    for option in new_options:
        single=orig_list.copy()
        single[elem_num]=option
        ret.append(single)
    return ret

class ProductionTree:
    def __init__(self,leaves=[],rule_used=None):
        self.leaves=leaves #these can either be symbols or production trees
        self.rule_used=rule_used

    def is_finished(self):
        for leaf in self.leaves:
            if isinstance(leaf,ProductionTree):
                if not leaf.is_finished():
                    return False
            elif not leaf.is_terminal():
                return False
        return True
    
    def count_production_use(self,production:Production):
        counter=0
        if self.rule_used is not None:
            #print("str(production) is {}".format(str(production)))
            #print("str(self.rule_used) is {}".format(str(self.rule_used)))
            if str(production)==str(self.rule_used):
                counter+=1
        for leaf in self.leaves:
            if isinstance(leaf,ProductionTree):
                counter+=leaf.count_production_use(production)
        return counter
    
    def __str__(self):
        ret=""
        for leaf in self.leaves:
            if isinstance(leaf,Symbol):
                if leaf.is_terminal():
                    ret+=leaf.rep
                else:
                    ret+="*"+leaf.rep+"*"
            else:
                ret+=str(leaf)
        return ret


class SearchProducer:
    def __init__(self,productions={}):
        if isinstance(productions,list):
            self.productions={}
            for p in productions:
                self.add_production(p)
            return
        if not isinstance(productions,dict):
            raise Exception("productions must be a dictionary")
        self.productions=productions # dictionary of symbol -> production

    def add_production(self,production):
        if production.lhs in self.productions:
            self.productions[production.lhs].append(production)
        else:
            self.productions[production.lhs]=[ production ]
            
    def load_string(self,s:str):
        for line in s.splitlines():
            if len(line)==0 or line[0]=='#':
                continue
            p=Production(line)
            self.add_production(p)

    def produce(self,start_string:str):
        my_usage={}
        #should I always assume we start with a nonterminal?
        start_symbol=Symbol(start_string,False)
        start_tree=ProductionTree([start_symbol])
        open_list=[start_tree]
        #while solution not found
        #take partial solution off of the open list
        #generate all possible single-step productions
        #add all single-step productions onto the open list in a sorted way
        while len(open_list)>0:
            on_tree=open_list.pop(0)
            if on_tree.is_finished():
                return on_tree
            next_trees=self.single_step(on_tree)
            open_list.extend(next_trees)

    def produce_all(self,start_string:str):
        print("start string is {}".format(start_string))
        my_usage={}
        #should I always assume we start with a nonterminal?
        start_symbol=Symbol(start_string,False)
        start_tree=ProductionTree([start_symbol])
        print("start tree is {}".format(str(start_tree)))
        open_list=[start_tree]
        #while solution not found
        #take partial solution off of the open list
        #generate all possible single-step productions
        #add all single-step productions onto the open list in a sorted way
        ret=[]
        while len(open_list)>0:
            print("open list is {}".format([str(tree) for tree in open_list]))
            on_tree=open_list.pop(0)
            if on_tree.is_finished():
                ret.append(on_tree)
            else:
                next_trees=self.single_step(on_tree,on_tree)
                open_list.extend(next_trees)
        return ret
                        
    def single_step(self,on_tree:ProductionTree,top_tree:ProductionTree=None):
        #return a list of possible productions
        if isinstance(on_tree,Symbol):
            if on_tree.is_terminal():
                return []
            else:
                new_leaves=[]
                if on_tree not in self.productions:
                    raise Exception("no productions for {}".format(on_tree.rep))
                for prod in self.productions[on_tree]:
                    my_count=top_tree.count_production_use(prod)
                    #print("prod is {}, count is {}".format(prod,my_count))
                    #print("max usage is {}".format(prod.max_usage))
                    if prod.max_usage==-1 or my_count<prod.max_usage:
                        new_leaves.append(ProductionTree(prod.rhs,prod))
                return new_leaves
        else: #otherwise it is a tree
            #walk through my leaves until I find an option
            for i in range(len(on_tree.leaves)):
                replacement=self.single_step(on_tree.leaves[i],top_tree=top_tree)
                if len(replacement)!=0:
                    new_leaves=expand_list(on_tree.leaves,i,replacement)
                    return [ ProductionTree(leaves) for leaves in new_leaves ]
        return []