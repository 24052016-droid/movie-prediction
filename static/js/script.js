const movieInput=document.getElementById("movieInput");
const recommendBtn=document.getElementById("recommendBtn");
const message=document.getElementById("message");
const movieContainer=document.getElementById("movieContainer");
const industryFilter=document.getElementById("industryFilter");
const languageFilter=document.getElementById("languageFilter");
const genreFilter=document.getElementById("genreFilter");
const resultsCount=document.getElementById("resultsCount");

function createCard(movie,index){
    const card=document.createElement("article");
    card.className="movie-card";
    card.style.animationDelay=`${index*.1}s`;

    const posterWrap=document.createElement("div");
    posterWrap.className="poster-wrap";

    if(movie.poster){
        const img=document.createElement("img");
        img.className="movie-poster";
        img.src=movie.poster;
        img.alt=movie.title+" movie poster";
        img.loading="lazy";
        img.onerror=()=>{
            posterWrap.innerHTML="";
            const fallback=document.createElement("div");
            fallback.className="poster-fallback";
            fallback.innerHTML=`<strong></strong><small>CINEMATIC DISCOVERY</small>`;
            fallback.querySelector("strong").textContent=movie.title;
            posterWrap.appendChild(fallback);
        };
        posterWrap.appendChild(img);
    }else{
        const fallback=document.createElement("div");
        fallback.className="poster-fallback";
        const title=document.createElement("strong");
        title.textContent=movie.title;
        const label=document.createElement("small");
        label.textContent="CINEMATIC DISCOVERY";
        fallback.append(title,label);
        posterWrap.appendChild(fallback);
    }

    const info=document.createElement("div");
    info.className="movie-info";

    const number=document.createElement("p");
    number.className="movie-number";
    number.textContent=`FILM 0${index+1}`;

    const title=document.createElement("h3");
    title.textContent=movie.title;

    const meta=document.createElement("p");
    meta.className="movie-meta";
    meta.textContent=[
        movie.industry,
        movie.language!=="Unknown"?movie.language:"",
        ...(movie.genres||[]).slice(0,2)
    ].filter(Boolean).join(" · ");

    const score=document.createElement("p");
    score.className="movie-score";
    score.textContent=`CONTENT SIMILARITY · ${movie.similarity}%`;

    info.append(number,title,meta,score);
    card.append(posterWrap,info);

    card.addEventListener("mousemove",event=>{
        if(window.matchMedia("(hover: none)").matches)return;
        const rect=card.getBoundingClientRect();
        const x=event.clientX-rect.left;
        const y=event.clientY-rect.top;
        const rotateX=((y/rect.height)-.5)*-7;
        const rotateY=((x/rect.width)-.5)*7;
        card.style.transform=`perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
    });

    card.addEventListener("mouseleave",()=>{
        card.style.transform="";
    });

    return card;
}

function displayMovies(movies){
    movieContainer.innerHTML="";
    resultsCount.textContent=`${movies.length} FILMS`;

    if(!movies.length){
        movieContainer.innerHTML='<div class="empty-state"><h3>No matching films found.</h3><p>Try changing your filters.</p></div>';
        return;
    }

    movies.forEach((movie,index)=>{
        movieContainer.appendChild(createCard(movie,index));
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
    message.textContent="Exploring cinematic similarities...";
    movieContainer.innerHTML='<div class="empty-state"><h3>Finding your next film...</h3><p>Please wait.</p></div>';

    try{
        const response=await fetch("/recommend",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                movie:movieName,
                industry:industryFilter.value,
                language:languageFilter.value,
                genre:genreFilter.value
            })
        });

        const data=await response.json();

        if(!response.ok)throw new Error(data.error||"Unable to find recommendations.");

        displayMovies(data.recommendations);
        message.textContent=`Films selected for ${data.movie}.`;
    }catch(error){
        message.textContent=error.message;
        movieContainer.innerHTML='<div class="empty-state"><h3>Discovery interrupted.</h3><p>Check the movie title and try again.</p></div>';
        resultsCount.textContent="0 FILMS";
    }finally{
        recommendBtn.disabled=false;
        recommendBtn.innerHTML='Discover <span>→</span>';
    }
}

recommendBtn.addEventListener("click",recommendMovie);

movieInput.addEventListener("keydown",event=>{
    if(event.key==="Enter")recommendMovie();
});

movieInput.addEventListener("input",()=>{
    message.textContent="Enter a film title to begin.";
});