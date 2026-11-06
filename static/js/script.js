const movieInput=document.getElementById("movieInput");
const recommendBtn=document.getElementById("recommendBtn");
const message=document.getElementById("message");
const movieContainer=document.getElementById("movieContainer");

function displayMovies(movies){
movieContainer.innerHTML="";
movies.forEach((movie,index)=>{
const card=document.createElement("article");
card.className="movie-card";
card.style.animationDelay=`${index*0.12}s`;
const posterWrap=document.createElement("div");
posterWrap.className="poster-wrap";
if(movie.poster){
const img=document.createElement("img");
img.className="movie-poster";
img.src=movie.poster;
img.alt=movie.title;
img.loading="lazy";
img.onerror=()=>{posterWrap.innerHTML='<div class="poster-fallback">✦</div>';};
posterWrap.appendChild(img);
}else{
posterWrap.innerHTML='<div class="poster-fallback">✦</div>';
}
const info=document.createElement("div");
info.className="movie-info";
const number=document.createElement("p");
number.className="movie-number";
number.textContent=`FILM 0${index+1}`;
const title=document.createElement("h3");
title.textContent=movie.title;
const score=document.createElement("p");
score.textContent=`Similarity: ${movie.similarity}%`;
info.append(number,title,score);
card.append(posterWrap,info);
movieContainer.appendChild(card);
card.addEventListener("mousemove",event=>{
if(window.matchMedia("(hover: none)").matches)return;
const rect=card.getBoundingClientRect();
const x=event.clientX-rect.left;
const y=event.clientY-rect.top;
const rotateX=((y/rect.height)-.5)*-9;
const rotateY=((x/rect.width)-.5)*9;
card.style.transform=`perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-7px)`;
});
card.addEventListener("mouseleave",()=>{
card.style.transform="";
});
});
}

async function recommendMovie(){
const movieName=movieInput.value.trim();
if(!movieName){
message.textContent="Please enter a movie title first.";
movieInput.focus();
return;
}
recommendBtn.disabled=true;
recommendBtn.textContent="Discovering...";
message.textContent="✦ Exploring cinematic similarities...";
movieContainer.innerHTML='<div class="empty-state"><div class="empty-icon">✦</div><h3>Discovering your next film...</h3><p>Please wait while the recommendation engine works.</p></div>';
try{
const response=await fetch("/recommend",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({movie:movieName})
});
const data=await response.json();
if(!response.ok)throw new Error(data.error||"Unable to find recommendations.");
displayMovies(data.recommendations);
message.textContent=`✦ Films selected for ${data.movie}`;
if(!data.recommendations.length){
movieContainer.innerHTML='<div class="empty-state"><h3>No recommendations found.</h3><p>Try another movie title.</p></div>';
}
}catch(error){
message.textContent=error.message;
movieContainer.innerHTML='<div class="empty-state"><div class="empty-icon">✧</div><h3>Discovery interrupted.</h3><p>Please check the movie title and try again.</p></div>';
}finally{
recommendBtn.disabled=false;
recommendBtn.innerHTML='Discover <span>✦</span>';
}
}

recommendBtn.addEventListener("click",recommendMovie);
movieInput.addEventListener("keydown",event=>{
if(event.key==="Enter")recommendMovie();
});
movieInput.addEventListener("input",()=>{
message.textContent="";
});