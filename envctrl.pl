% Prolog predicates used to make decisions

/*  
    This file is part of pyswip_envctrl.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

inBounds(Upperbound, Lowerbound, X, Result) :-
	X > Upperbound,
	Result is Upperbound, !.
inBounds(Upperbound, Lowerbound, X, Result) :-
	X < Lowerbound,
	Result is Lowerbound, !.
inBounds(Upperbound, Lowerbound, X, Result) :-
	X =< Upperbound,
	X >= Lowerbound,
	Result is X, !.

setto(Outside, Average, Upperbound, Lowerbound, Savings, Yield, Write) :-
	% If both the average and the outside conditions are above the bounds,
	Average > Upperbound,
	Outside > Upperbound,
	inBounds(Upperbound, Lowerbound, Average, Yield),
	append("The goal could not be achieved. Outside conditions and user preferences are extremely high.","",Write), !.
setto(Outside, Average, Upperbound, Lowerbound, Savings, Yield, Write) :-
	% or below the bounds, force the yield into the bounds. Savings % doesn't matter.
	Average < Lowerbound,
	Outside < Lowerbound,
	inBounds(Upperbound, Lowerbound, Average, Yield),
	append("The goal could not be achieved. Outside conditions and user preferences are extremely low.","",Write), !.
setto(Outside, Average, Upperbound, Lowerbound, Savings, Yield, Write) :-
	% Otherwise, find the yield, but make sure it is bounded.
	savings(Outside, Average, Savings, Unbounded),
	inBounds(Upperbound, Lowerbound, Unbounded, Yield),
	\+ Unbounded == Yield,
	append("The goal result is out of bounds. Result has been rebounded.","",Write), !.
setto(Outside, Average, Upperbound, Lowerbound, Savings, Yield, Write) :-
	savings(Outside, Average, Savings, Unbounded),
	inBounds(Upperbound, Lowerbound, Unbounded, Yield),
	append("The goal was achieved.","",Write), !.

savings(Outside, Average, Savings, Yield) :-
	\+ Average == Outside,
	Outside > Average,
	abs(Outside-Average, Delta),
	abs(Outside - (Delta * (1 - (Savings / 100))), Yield).
savings(Outside, Average, Savings, Yield) :-
	\+ Average == Outside,
	Outside < Average,
	abs(Outside-Average, Delta),
	abs(Outside + (Delta * (1 - (Savings / 100))), Yield).
savings(Outside, Outside, Savings, Yield) :-
	Average == Outside,
	Yield is Outside.

something(X,Y,W) :- Y is X, append("hi","",W).
	